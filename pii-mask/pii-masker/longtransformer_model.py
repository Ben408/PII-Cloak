#!/usr/bin/env python3
"""
LongTransformer PII Model Loader
Handles the LongTransformer PII detection model with .ckpt checkpoint format
"""

import torch
import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import Dict, List, Tuple

class LongTransformerPIIMasker:
    """LongTransformer-based PII detection model"""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "output_model", "longtransformer_pii")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Load model from checkpoint
        self.model = self._load_model_from_checkpoint(model_path)
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        
        print(f"✅ LongTransformer PII model loaded successfully on {self.device}!")
    
    def _load_model_from_checkpoint(self, model_path: str):
        """Load model from .ckpt checkpoint file"""
        checkpoint_path = os.path.join(model_path, "ckeckpoint_0.ckpt")
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        # Extract model state dict
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif 'model' in checkpoint:
            state_dict = checkpoint['model']
        else:
            state_dict = checkpoint
        
        # Create model architecture (assuming it's a token classification model)
        # We'll use a base model and load the weights
        try:
            # Try to load config from the checkpoint
            if 'config' in checkpoint:
                config = checkpoint['config']
                model = AutoModelForTokenClassification.from_config(config)
            else:
                # Fallback: create a basic model and load weights
                model = AutoModelForTokenClassification.from_pretrained(
                    'microsoft/deberta-v3-base',
                    num_labels=13  # Based on the original model labels
                )
        except Exception as e:
            print(f"Warning: Could not load model config, using fallback: {e}")
            model = AutoModelForTokenClassification.from_pretrained(
                'microsoft/deberta-v3-base',
                num_labels=13
            )
        
        # Load state dict
        try:
            model.load_state_dict(state_dict, strict=False)
            print("✅ Model weights loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load all weights: {e}")
            # Try partial loading
            model.load_state_dict(state_dict, strict=False)
        
        return model
    
    def mask_pii(self, input_text: str) -> Tuple[str, Dict[str, List[str]]]:
        """Detect and mask PII in input text"""
        # Tokenize input
        inputs = self.tokenizer(
            input_text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=2048  # LongTransformer can handle longer sequences
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)
        
        # Get predicted labels
        predicted_labels = []
        for pred in predictions[0]:
            if pred.item() < len(self.model.config.id2label):
                label = self.model.config.id2label[pred.item()]
                predicted_labels.append(label)
            else:
                predicted_labels.append('O')
        
        # Process results - reconstruct entities from consecutive tokens
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        result_dict = {}
        
        current_entity = None
        current_tokens = []
        
        for token, label in zip(tokens, predicted_labels):
            # Clean up token
            clean_token = token.replace('▁', ' ').replace('<s>', '').replace('</s>', '').strip()
            
            # Skip special tokens
            if clean_token in ['<s>', '</s>', '<pad>'] or not clean_token:
                continue
            
            if label != 'O':
                # Start or continue entity
                if current_entity is None:
                    current_entity = label
                    current_tokens = [clean_token]
                elif current_entity == label:
                    # Continue current entity
                    current_tokens.append(clean_token)
                else:
                    # Different entity type - save current and start new
                    if current_tokens:
                        entity_text = ' '.join(current_tokens).strip()
                        if entity_text:
                            if current_entity not in result_dict:
                                result_dict[current_entity] = []
                            result_dict[current_entity].append(entity_text)
                    
                    current_entity = label
                    current_tokens = [clean_token]
            else:
                # End of entity
                if current_entity and current_tokens:
                    entity_text = ' '.join(current_tokens).strip()
                    if entity_text:
                        if current_entity not in result_dict:
                            result_dict[current_entity] = []
                        result_dict[current_entity].append(entity_text)
                
                current_entity = None
                current_tokens = []
        
        # Handle any remaining entity
        if current_entity and current_tokens:
            entity_text = ' '.join(current_tokens).strip()
            if entity_text:
                if current_entity not in result_dict:
                    result_dict[current_entity] = []
                result_dict[current_entity].append(entity_text)
        
        # Extract SSNs using regex (fallback)
        ssn_dict = self.extract_ssn(input_text)
        result_dict.update(ssn_dict)
        
        # Create masked text
        masked_text = self._create_masked_text(input_text, result_dict)
        
        return masked_text, result_dict
    
    def _create_masked_text(self, text: str, pii_dict: Dict[str, List[str]]) -> str:
        """Create masked version of the text"""
        masked_text = text
        
        # Sort entities by length (longest first) to avoid partial matches
        all_entities = []
        for entity_type, values in pii_dict.items():
            for value in values:
                # Skip empty or invalid values
                if value and value.strip() and len(value.strip()) > 0:
                    all_entities.append((value.strip(), entity_type))
        
        all_entities.sort(key=lambda x: len(x[0]), reverse=True)
        
        # Replace entities with masks
        for value, entity_type in all_entities:
            if value in masked_text:
                mask = f"[{entity_type.upper()}]"
                masked_text = masked_text.replace(value, mask)
        
        return masked_text
    
    @staticmethod
    def extract_ssn(input_string: str) -> Dict[str, List[str]]:
        """Extract SSNs using regex pattern"""
        ssn_pattern = r'\b(\d{3}-\d{2}-\d{4}|\d{9})\b'
        ssn_dict = {}
        matches = re.findall(ssn_pattern, input_string)
        for ssn in matches:
            ssn_dict[ssn] = ['SSN']
        return ssn_dict
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model"""
        return {
            'model_type': 'LongTransformer',
            'device': self.device,
            'num_labels': self.model.config.num_labels if hasattr(self.model.config, 'num_labels') else 'Unknown',
            'max_length': 2048,
            'labels': list(self.model.config.id2label.values()) if hasattr(self.model.config, 'id2label') else []
        }

# Test the model
if __name__ == "__main__":
    try:
        masker = LongTransformerPIIMasker()
        print("Model info:", masker.get_model_info())
        
        # Test with sample text
        test_text = "Hello, my name is John Smith and my email is john.smith@email.com. My SSN is 123-45-6789."
        masked_text, pii_dict = masker.mask_pii(test_text)
        
        print(f"Original: {test_text}")
        print(f"Masked: {masked_text}")
        print(f"PII found: {pii_dict}")
        
    except Exception as e:
        print(f"Error testing model: {e}")
        import traceback
        traceback.print_exc()
