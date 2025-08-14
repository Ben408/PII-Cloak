#!/usr/bin/env python3
"""
PII Detection Engine for Cloak & Style
Combines rule-based detection with ML-based detection using PII Masker
"""

import re
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Add the pii-mask directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pii-mask', 'pii-masker'))

@dataclass
class PIIEntity:
    """Represents a detected PII entity"""
    entity_type: str
    value: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    detection_method: str = "rule_based"
    status: str = "auto_masked"  # auto_masked, accepted, rejected, ignored, questionable

@dataclass
class DetectionResult:
    """Result of PII detection on text"""
    entities_found: List[PIIEntity]
    masked_content: str
    original_text: str
    processing_time: float
    questionable_entities: List[PIIEntity] = None
    residual_entities: List[PIIEntity] = None

class PIIDetectionEngine:
    """Combines rule-based and ML-based PII detection"""
    
    def __init__(self, config: Optional[Dict] = None):
        # Default configuration based on product requirements
        self.config = config or {
            "language": "en",
            "entities": ["PERSON", "ADDRESS", "EMAIL", "PHONE", "IP", "CREDIT_CARD", 
                        "BANK_ACCT", "NATIONAL_ID", "DOB", "USERNAME", "GEO"],
            "mask_format": "TOKEN",
            "review_queue": False,
            "dry_run": False,
            "caps": {"pdf_pages": 100, "pdf_mb": 10, "rows": 100000},
            "reports": ["html", "json"],
            "validation": {
                "residual_action": "warn", 
                "min_confidence": 0.35, 
                "questionable_band": [0.35, 0.65]
            },
            "backend": "pii-masker"
        }
        
        self.ml_detector = None
        self.longtransformer_detector = None
        self.fallback_ner_model = None
        self.base_deberta = None
        
        # Try to load the LongTransformer PII model first (newest and most capable)
        try:
            from longtransformer_model import LongTransformerPIIMasker
            self.longtransformer_detector = LongTransformerPIIMasker()
            print("✅ LongTransformer PII model loaded successfully!")
        except Exception as e:
            print(f"⚠️ LongTransformer PII model not available: {e}")
            
            # Try to load the custom PII model second
            try:
                from model import PIIMasker
                self.ml_detector = PIIMasker()
                print("✅ Custom PII model loaded successfully!")
            except Exception as e2:
                print(f"⚠️ Custom PII model not available: {e2}")
                print("🔄 Attempting to load fallback models...")
                
                # Try to load BERT NER model as fallback
                try:
                    from transformers import AutoTokenizer, AutoModelForTokenClassification
                    self.fallback_ner_model = AutoModelForTokenClassification.from_pretrained('dslim/bert-base-NER')
                    self.fallback_tokenizer = AutoTokenizer.from_pretrained('dslim/bert-base-NER')
                    print("✅ BERT NER fallback model loaded successfully!")
                except Exception as e3:
                    print(f"⚠️ BERT NER fallback model not available: {e3}")
                    
                    # Try to load base DeBERTa model
                    try:
                        self.base_deberta = AutoModelForTokenClassification.from_pretrained('microsoft/deberta-v3-base')
                        self.base_tokenizer = AutoTokenizer.from_pretrained('microsoft/deberta-v3-base')
                        print("✅ Base DeBERTa model loaded successfully!")
                    except Exception as e4:
                        print(f"⚠️ Base DeBERTa model not available: {e4}")
                        print("🔄 Falling back to rule-based detection only")
        
        # Rule-based patterns
        self.patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b(?!\d)',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'CREDIT_CARD': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'URL': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'ZIP_CODE': r'\b\d{5}(?:-\d{4})?\b'
        }
        
        # Validation functions
        self.validators = {
            'CREDIT_CARD': self._luhn_check,
            'IP_ADDRESS': self._validate_ip,
            'SSN': self._validate_ssn
        }
        
        # Structured entities that must be fully masked (no partial reveal)
        self.structured_entities = {
            'EMAIL', 'CREDIT_CARD', 'PHONE', 'IP_ADDRESS', 'SSN', 'NATIONAL_ID',
            'BANK_ACCT', 'IP'
        }
        
        # Free-text entities that can have partial reveal
        self.free_text_entities = {
            'PERSON', 'BRAND', 'ADDRESS', 'USERNAME', 'GEO'
        }
    
    def detect_pii(self, text: str) -> DetectionResult:
        """Detect PII in text using both rule-based and ML methods"""
        import time
        start_time = time.time()
        
        # Rule-based detection
        rule_entities = self._detect_rule_based(text)
        
        # ML-based detection
        ml_entities = self._detect_ml(text)
        
        # Combine and resolve entities with proper fusion logic
        all_entities = self._fuse_and_resolve_entities(rule_entities, ml_entities)
        
        # Mark questionable entities based on confidence band
        questionable_entities = self._mark_questionable_entities(all_entities)
        
        # Create masked content
        masked_content = self._mask_text(text, all_entities)
        
        # Validate for residual PII
        residual_entities = self._validate_residual_pii(masked_content)
        
        processing_time = time.time() - start_time
        
        return DetectionResult(
            entities_found=all_entities,
            masked_content=masked_content,
            original_text=text,
            processing_time=processing_time,
            questionable_entities=questionable_entities,
            residual_entities=residual_entities
        )
    
    def _detect_rule_based(self, text: str) -> List[PIIEntity]:
        """Detect PII using regex patterns and validation"""
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                value = match.group()
                
                # Apply validation if available
                if entity_type in self.validators:
                    if not self.validators[entity_type](value):
                        continue
                
                entities.append(PIIEntity(
                    entity_type=entity_type,
                    value=value,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=1.0,  # High confidence for rule-based detection
                    detection_method="rule_based",
                    status="auto_masked"
                ))
        
        return entities
    
    def _detect_ml(self, text: str) -> List[PIIEntity]:
        """Detect PII using ML models"""
        entities = []
        
        # Try LongTransformer PII model first (most capable)
        if self.longtransformer_detector:
            try:
                masked_text, pii_dict = self.longtransformer_detector.mask_pii(text)
                # Convert PII dict to entities
                for entity_type, values in pii_dict.items():
                    for value in values:
                        # Find position in original text
                        start_pos = text.find(value)
                        if start_pos != -1:
                            # Map generic labels to meaningful PII types
                            mapped_type = self._map_ml_label_to_pii_type(entity_type)
                            if mapped_type:
                                entities.append(PIIEntity(
                                    entity_type=mapped_type,
                                    value=value,
                                    start_pos=start_pos,
                                    end_pos=start_pos + len(value),
                                    confidence=0.85,  # ML confidence
                                    detection_method="longtransformer_pii",
                                    status="auto_masked"
                                ))
                
                # Filter out low-quality detections
                entities = self._filter_ml_entities(entities)
                
                # Improve entity classification
                for entity in entities:
                    entity = self._improve_entity_classification(entity)
                
                # Filter out non-PII entities
                entities = [e for e in entities if e.entity_type not in ['GREETING', 'FIELD_LABEL', 'PRONOUN']]
                
                return entities
            except Exception as e:
                print(f"⚠️ LongTransformer PII model failed: {e}")
        
        # Try custom PII model second
        if self.ml_detector:
            try:
                masked_text, pii_dict = self.ml_detector.mask_pii(text)
                # Convert PII dict to entities
                for entity_type, values in pii_dict.items():
                    for value in values:
                        # Find position in original text
                        start_pos = text.find(value)
                        if start_pos != -1:
                            entities.append(PIIEntity(
                                entity_type=entity_type.upper(),
                                value=value,
                                start_pos=start_pos,
                                end_pos=start_pos + len(value),
                                confidence=0.8,
                                detection_method="custom_pii_model",
                                status="auto_masked"
                            ))
                return entities
            except Exception as e:
                print(f"⚠️ Custom PII model failed: {e}")
        
        # Try BERT NER fallback
        if self.fallback_ner_model:
            try:
                entities.extend(self._detect_with_bert_ner(text))
                return entities
            except Exception as e:
                print(f"⚠️ BERT NER model failed: {e}")
        
        # Try base DeBERTa (limited functionality)
        if self.base_deberta:
            try:
                entities.extend(self._detect_with_base_deberta(text))
                return entities
            except Exception as e:
                print(f"⚠️ Base DeBERTa model failed: {e}")
        
        return entities
    
    def _map_ml_label_to_pii_type(self, label: str) -> Optional[str]:
        """Map generic ML labels to meaningful PII types"""
        # Map generic labels to PII types based on context
        # Based on the LongTransformer model's label scheme and observed output
        label_mapping = {
            'LABEL_0': 'EMAIL',
            'LABEL_1': 'ID_NUM',
            'LABEL_2': 'PERSON',
            'LABEL_3': 'PERSON',
            'LABEL_4': 'PERSON',
            'LABEL_5': 'PERSON',
            'LABEL_6': 'USERNAME',
            'LABEL_7': 'PERSON',
            'LABEL_8': 'PERSON',
            'LABEL_9': 'PHONE',
            'LABEL_10': 'ADDRESS',
            'LABEL_11': 'PERSON',
            'LABEL_12': 'URL'
        }
        return label_mapping.get(label)
    
    def _improve_entity_classification(self, entity: PIIEntity) -> PIIEntity:
        """Improve entity classification based on value content"""
        value = entity.value.lower().strip()
        
        # Reclassify based on content patterns
        if '@' in value and '.' in value:
            entity.entity_type = 'EMAIL'
        elif value.isdigit() and len(value) >= 4:
            entity.entity_type = 'ID_NUM'
        elif value in ['hello', 'hi', 'hey']:
            entity.entity_type = 'GREETING'  # Not PII
        elif value in ['email', 'phone', 'address', 'name']:
            entity.entity_type = 'FIELD_LABEL'  # Not PII
        elif value in ['my', 'i', 'me']:
            entity.entity_type = 'PRONOUN'  # Not PII
        
        return entity
    
    def _filter_ml_entities(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """Filter out low-quality ML detections"""
        filtered = []
        for entity in entities:
            # Skip single characters and punctuation
            if len(entity.value.strip()) <= 1:
                continue
            
            # Skip common punctuation and whitespace
            if entity.value.strip() in [',', '.', ':', ';', '!', '?', ' ', '\n', '\t']:
                continue
            
            # Skip very short tokens that are likely noise
            if len(entity.value.strip()) < 2:
                continue
            
            # Skip tokens that are just numbers (likely not PII)
            if entity.value.strip().isdigit() and len(entity.value.strip()) < 4:
                continue
            
            filtered.append(entity)
        
        return filtered
    
    def _fuse_and_resolve_entities(self, rule_entities: List[PIIEntity], 
                                  ml_entities: List[PIIEntity]) -> List[PIIEntity]:
        """Fuse rule-based and ML entities with proper precedence"""
        all_entities = rule_entities + ml_entities
        
        if not all_entities:
            return []
        
        # Sort by start position
        all_entities.sort(key=lambda x: x.start_pos)
        
        resolved = []
        for entity in all_entities:
            # Check for overlaps with existing entities
            overlap = False
            for existing in resolved:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    overlap = True
                    # Prefer rule-based over ML (deterministic rules take precedence)
                    if (entity.detection_method == "rule_based" and 
                        existing.detection_method != "rule_based"):
                        resolved.remove(existing)
                        resolved.append(entity)
                    elif (entity.detection_method == "rule_based" and 
                          existing.detection_method == "rule_based"):
                        # If both are rule-based, keep the one with higher confidence
                        if entity.confidence > existing.confidence:
                            resolved.remove(existing)
                            resolved.append(entity)
                    break
            
            if not overlap:
                resolved.append(entity)
        
        return resolved
    
    def _mark_questionable_entities(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """Mark entities in the questionable confidence band"""
        min_conf = self.config['validation']['min_confidence']
        max_conf = self.config['validation']['questionable_band'][1]
        
        questionable = []
        for entity in entities:
            if min_conf <= entity.confidence <= max_conf:
                entity.status = "questionable"
                questionable.append(entity)
        
        return questionable
    
    def _validate_residual_pii(self, masked_text: str) -> List[PIIEntity]:
        """Validate that no PII remains in the masked output"""
        # Re-scan the masked content for any remaining PII
        residual_entities = []
        
        # Check for any remaining PII patterns
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, masked_text, re.IGNORECASE)
            for match in matches:
                value = match.group()
                # Apply validation if available
                if entity_type in self.validators:
                    if not self.validators[entity_type](value):
                        continue
                
                residual_entities.append(PIIEntity(
                    entity_type=entity_type,
                    value=value,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=1.0,
                    detection_method="residual_validation",
                    status="residual"
                ))
        
        return residual_entities
    
    def _detect_with_bert_ner(self, text: str) -> List[PIIEntity]:
        """Detect entities using BERT NER model"""
        entities = []
        
        # Tokenize and predict
        inputs = self.fallback_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.fallback_ner_model(**inputs)
        
        # Get predictions
        predictions = outputs.logits.argmax(dim=-1)[0]
        tokens = self.fallback_tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        # Map BERT NER labels to our entity types
        label_mapping = {
            'B-PER': 'PERSON',
            'I-PER': 'PERSON',
            'B-ORG': 'ORGANIZATION',
            'I-ORG': 'ORGANIZATION',
            'B-LOC': 'LOCATION',
            'I-LOC': 'LOCATION'
        }
        
        current_entity = None
        current_value = ""
        current_start = 0
        
        for i, (token, pred) in enumerate(zip(tokens, predictions)):
            label = self.fallback_ner_model.config.id2label[pred.item()]
            
            if label.startswith('B-'):
                # Save previous entity if exists
                if current_entity:
                    entities.append(PIIEntity(
                        entity_type=current_entity,
                        value=current_value.strip(),
                        start_pos=current_start,
                        end_pos=current_start + len(current_value),
                        confidence=0.8,
                        detection_method="bert_ner",
                        status="auto_masked"
                    ))
                
                # Start new entity
                entity_type = label_mapping.get(label, 'UNKNOWN')
                if entity_type != 'UNKNOWN':
                    current_entity = entity_type
                    current_value = token.replace('##', '')
                    current_start = i
            
            elif label.startswith('I-') and current_entity:
                current_value += " " + token.replace('##', '')
            
            elif label == 'O' and current_entity:
                # End of entity
                entities.append(PIIEntity(
                    entity_type=current_entity,
                    value=current_value.strip(),
                    start_pos=current_start,
                    end_pos=current_start + len(current_value),
                    confidence=0.8,
                    detection_method="bert_ner",
                    status="auto_masked"
                ))
                current_entity = None
                current_value = ""
        
        return entities
    
    def _detect_with_base_deberta(self, text: str) -> List[PIIEntity]:
        """Detect entities using base DeBERTa (limited functionality)"""
        # Base DeBERTa is not fine-tuned for NER, so we'll use it for basic text analysis
        # This is a fallback that provides minimal entity detection
        entities = []
        
        # Simple heuristic: look for capitalized words that might be names
        words = text.split()
        for i, word in enumerate(words):
            if (word[0].isupper() and len(word) > 2 and 
                not word.endswith('.') and not word.endswith(',') and
                not any(char.isdigit() for char in word)):
                
                # Simple validation: not at start of sentence, not common words
                common_words = {'The', 'This', 'That', 'These', 'Those', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
                if word not in common_words:
                    start_pos = text.find(word)
                    entities.append(PIIEntity(
                        entity_type='POTENTIAL_NAME',
                        value=word,
                        start_pos=start_pos,
                        end_pos=start_pos + len(word),
                        confidence=0.3,
                        detection_method="base_deberta_heuristic",
                        status="auto_masked"
                    ))
        
        return entities
    
    def _mask_text(self, text: str, entities: List[PIIEntity]) -> str:
        """Mask detected PII entities in text with proper policy enforcement"""
        if not entities:
            return text
        
        # Sort entities by start position (descending) to avoid index shifting
        entities.sort(key=lambda x: x.start_pos, reverse=True)
        
        masked_text = text
        token_counter = {}
        
        for entity in entities:
            # Initialize counter for this entity type
            if entity.entity_type not in token_counter:
                token_counter[entity.entity_type] = 1
            else:
                token_counter[entity.entity_type] += 1
            
            # Create token based on entity type and masking policy
            if entity.entity_type in self.structured_entities:
                # Structured entities must be fully masked (no partial reveal)
                mask = f"[{entity.entity_type.upper()}_{token_counter[entity.entity_type]:03d}]"
            elif entity.entity_type in self.free_text_entities:
                # Free-text entities can have partial reveal if configured
                if self.config.get('mask_format') == 'PARTIAL_REVEAL':
                    # Partial reveal (e.g., "John" -> "J***")
                    if len(entity.value) > 1:
                        mask = entity.value[0] + '*' * (len(entity.value) - 1)
                    else:
                        mask = '*'
                else:
                    # Default token format
                    mask = f"[{entity.entity_type.upper()}_{token_counter[entity.entity_type]:03d}]"
            else:
                # Default token format for unknown types
                mask = f"[{entity.entity_type.upper()}_{token_counter[entity.entity_type]:03d}]"
            
            # Apply masking
            masked_text = masked_text[:entity.start_pos] + mask + masked_text[entity.end_pos:]
        
        return masked_text
    
    def _luhn_check(self, number: str) -> bool:
        """Validate credit card number using Luhn algorithm"""
        # Remove non-digits
        digits = [int(d) for d in str(number) if d.isdigit()]
        
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        
        return checksum % 10 == 0
    
    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
        
        return True
    
    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format"""
        # Remove dashes
        clean_ssn = ssn.replace('-', '')
        
        if len(clean_ssn) != 9:
            return False
        
        # Check for invalid patterns
        if clean_ssn.startswith('000') or clean_ssn.startswith('666') or clean_ssn.startswith('9'):
            return False
        
        if clean_ssn[3:5] == '00' or clean_ssn[5:] == '0000':
            return False
        
        return True
    
    def get_detection_methods(self) -> List[str]:
        """Get list of available detection methods"""
        methods = ["rule_based"]
        
        if self.longtransformer_detector:
            methods.append("longtransformer_pii")
        if self.ml_detector:
            methods.append("custom_pii_model")
        if self.fallback_ner_model:
            methods.append("bert_ner")
        if self.base_deberta:
            methods.append("base_deberta_heuristic")
        
        return methods
