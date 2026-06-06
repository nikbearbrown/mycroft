"""
Patent Intelligence System - Data Processor
Advanced patent data processing with AI classification and enrichment.

Author: Darshan Rahul Rajopadhye
License: MIT
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Set
import pandas as pd
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessingConfig:
    """Configuration for patent processing."""
    ai_keywords: List[str] = None
    ai_cpc_prefixes: List[str] = None
    ai_ipc_codes: List[str] = None
    company_aliases: Dict[str, str] = None
    
    def __post_init__(self):
        if self.ai_keywords is None:
            self.ai_keywords = [
                "artificial intelligence", "neural network", "machine learning",
                "deep learning", "natural language processing", "computer vision",
                "reinforcement learning", "generative ai", "large language model",
                "transformer", "lstm", "cnn", "gan", "autoencoder", "bert", "gpt"
            ]
        
        if self.ai_cpc_prefixes is None:
            self.ai_cpc_prefixes = [
                "G06N",     # Computing arrangements based on specific computational models
                "G06F17",   # Digital computing or data processing equipment
                "G06F18",   # Pattern recognition; Image data processing
                "G06K9",    # Methods or arrangements for reading or recognising printed characters
                "G06F40",   # Handling natural language data
                "G10L15",   # Speech recognition
                "G10L25"    # Speech or voice analysis techniques
            ]
        
        if self.ai_ipc_codes is None:
            self.ai_ipc_codes = [
                "G06N3",    # Computing arrangements based on biological models
                "G06N5",    # Computing arrangements using knowledge-based models
                "G06N7",    # Computing arrangements based on specific mathematical models
                "G06N20"    # Machine learning
            ]
        
        if self.company_aliases is None:
            self.company_aliases = {
                "INTERNATIONAL BUSINESS MACHINES CORPORATION": "IBM",
                "ALPHABET INC.": "Google",
                "MICROSOFT CORPORATION": "Microsoft",
                "AMAZON TECHNOLOGIES, INC.": "Amazon",
                "META PLATFORMS, INC.": "Meta",
                "APPLE INC.": "Apple",
                "NVIDIA CORPORATION": "NVIDIA"
            }


class PatentProcessor:
    """Advanced patent data processor with AI classification."""
    
    def __init__(self, config: ProcessingConfig = None, logger: Optional[logging.Logger] = None):
        self.config = config or ProcessingConfig()
        self.logger = logger or self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up structured logging."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def safe_eval(self, data_str: str) -> List[Dict]:
        """Safely parse JSON-like strings from CSV."""
        if pd.isna(data_str) or data_str == '':
            return []
        
        try:
            # Handle string representation of lists
            if isinstance(data_str, str):
                # Clean up the string format
                data_str = data_str.strip()
                if data_str.startswith('[') and data_str.endswith(']'):
                    return ast.literal_eval(data_str)
                else:
                    # Try parsing as JSON
                    return json.loads(data_str)
            return data_str if isinstance(data_str, list) else []
        except (ValueError, SyntaxError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to parse data: {data_str[:100]}... Error: {e}")
            return []
    
    def extract_organization(self, assignee_field: Any) -> Optional[str]:
        """Extract primary organization from assignee data."""
        assignees = self.safe_eval(assignee_field) if isinstance(assignee_field, str) else assignee_field
        
        if not assignees or not isinstance(assignees, list):
            return None
        
        # Get the first assignee organization
        for assignee in assignees:
            if isinstance(assignee, dict):
                org = assignee.get("assignee_organization") or assignee.get("organization")
                if org:
                    # Normalize company name
                    org_clean = self.normalize_company_name(org)
                    return org_clean
        
        return None
    
    def normalize_company_name(self, company_name: str) -> str:
        """Normalize and clean company names."""
        if not company_name:
            return ""
        
        # Convert to uppercase for matching
        company_upper = company_name.upper().strip()
        
        # Check for known aliases
        for full_name, alias in self.config.company_aliases.items():
            if full_name in company_upper:
                return alias
        
        # Clean up common suffixes and patterns
        company_clean = re.sub(r'\s+(INC\.?|CORP\.?|CORPORATION|LLC|LTD\.?|CO\.?)$', '', company_upper)
        company_clean = re.sub(r'\s+', ' ', company_clean).strip()
        
        # Title case for better readability
        return company_clean.title()
    
    def extract_inventors(self, inventor_field: Any) -> str:
        """Extract and format inventor names."""
        inventors = self.safe_eval(inventor_field) if isinstance(inventor_field, str) else inventor_field
        
        if not inventors or not isinstance(inventors, list):
            return ""
        
        inventor_names = []
        for inv in inventors:
            if isinstance(inv, dict):
                first = inv.get('inventor_name_first', '') or ''
                last = inv.get('inventor_name_last', '') or ''
                full_name = f"{first} {last}".strip()
                if full_name:
                    inventor_names.append(full_name)
        
        return "; ".join(inventor_names)
    
    def extract_cpc_classes(self, cpc_field: Any) -> str:
        """Extract CPC classification codes."""
        cpcs = self.safe_eval(cpc_field) if isinstance(cpc_field, str) else cpc_field
        
        if not cpcs or not isinstance(cpcs, list):
            return ""
        
        cpc_codes = []
        for cpc in cpcs:
            if isinstance(cpc, dict):
                code = cpc.get("cpc_class_id") or cpc.get("class_id")
                if code:
                    cpc_codes.append(code)
        
        return "; ".join(sorted(set(cpc_codes)))
    
    def extract_wipo_fields(self, wipo_field: Any) -> str:
        """Extract WIPO field classifications."""
        wipos = self.safe_eval(wipo_field) if isinstance(wipo_field, str) else wipo_field
        
        if not wipos or not isinstance(wipos, list):
            return ""
        
        wipo_codes = []
        for wipo in wipos:
            if isinstance(wipo, dict):
                code = wipo.get("wipo_field_id") or wipo.get("field_id")
                if code:
                    wipo_codes.append(code)
        
        return "; ".join(sorted(set(wipo_codes)))
    
    def classify_ai_patent(self, title: str, abstract: str, cpc_field: Any) -> Dict[str, Any]:
        """
        Classify patent as AI-related with confidence scoring.
        
        Returns:
            Dict with is_ai, confidence_score, and matching_indicators
        """
        classification = {
            "is_ai": False,
            "confidence_score": 0.0,
            "matching_indicators": []
        }
        
        # Text-based classification
        text_content = f"{title or ''} {abstract or ''}".lower()
        
        # Check for AI keywords
        keyword_matches = []
        for keyword in self.config.ai_keywords:
            if keyword.lower() in text_content:
                keyword_matches.append(keyword)
        
        if keyword_matches:
            classification["matching_indicators"].extend(keyword_matches)
            classification["confidence_score"] += 0.3 + (len(keyword_matches) * 0.1)
        
        # CPC-based classification
        cpcs = self.safe_eval(cpc_field) if isinstance(cpc_field, str) else cpc_field
        cpc_matches = []
        
        if cpcs and isinstance(cpcs, list):
            for cpc in cpcs:
                if isinstance(cpc, dict):
                    cpc_id = cpc.get("cpc_class_id", "")
                    for prefix in self.config.ai_cpc_prefixes:
                        if cpc_id.startswith(prefix):
                            cpc_matches.append(cpc_id)
                            break
        
        if cpc_matches:
            classification["matching_indicators"].extend(cpc_matches)
            classification["confidence_score"] += 0.5 + (len(cpc_matches) * 0.1)
        
        # Final classification
        classification["is_ai"] = classification["confidence_score"] > 0.3
        classification["confidence_score"] = min(1.0, classification["confidence_score"])
        
        return classification
    
    def calculate_patent_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary metrics for the patent dataset."""
        metrics = {
            "total_patents": len(df),
            "ai_patents": len(df[df["is_ai"] == True]),
            "ai_percentage": (len(df[df["is_ai"] == True]) / len(df) * 100) if len(df) > 0 else 0,
            "top_organizations": df[df["organization"].notna()]["organization"].value_counts().head(10).to_dict(),
            "patent_years": df["patent_date"].str[:4].value_counts().sort_index().to_dict() if "patent_date" in df.columns else {},
            "avg_confidence_score": df[df["is_ai"] == True]["ai_confidence"].mean() if "ai_confidence" in df.columns else 0
        }
        
        return metrics
    
    def process_patents(self, 
                       input_file: str, 
                       output_file: str = None,
                       include_abstracts: bool = False) -> pd.DataFrame:
        """
        Process raw patent data into enriched format.
        
        Args:
            input_file: Path to raw patent CSV
            output_file: Path to save processed data
            include_abstracts: Whether to include abstract analysis
            
        Returns:
            Processed DataFrame
        """
        self.logger.info(f"Processing patents from {input_file}")
        
        # Load data
        df = pd.read_csv(input_file)
        self.logger.info(f"Loaded {len(df)} patent records")
        
        # Process fields
        processed_data = []
        
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                self.logger.info(f"Processed {idx}/{len(df)} records")
            
            # Extract basic fields
            record = {
                "patent_id": row.get("patent_id", ""),
                "patent_title": row.get("patent_title", ""),
                "patent_date": row.get("patent_date", ""),
                "organization": self.extract_organization(row.get("assignees", "")),
                "inventors": self.extract_inventors(row.get("inventors", "")),
                "cpc_classes": self.extract_cpc_classes(row.get("cpc_current", "")),
                "wipo_fields": self.extract_wipo_fields(row.get("wipo", "")),
            }
            
            # AI Classification
            abstract = row.get("patent_abstract", "") if include_abstracts else ""
            ai_classification = self.classify_ai_patent(
                record["patent_title"], 
                abstract,
                row.get("cpc_current", "")
            )
            
            record.update({
                "is_ai": ai_classification["is_ai"],
                "ai_confidence": ai_classification["confidence_score"],
                "ai_indicators": "; ".join(ai_classification["matching_indicators"])
            })
            
            processed_data.append(record)
        
        # Create processed DataFrame
        processed_df = pd.DataFrame(processed_data)
        
        # Calculate metrics
        metrics = self.calculate_patent_metrics(processed_df)
        self.logger.info(f"Processing complete: {metrics}")
        
        # Save results
        if output_file:
            processed_df.to_csv(output_file, index=False)
            self.logger.info(f"Processed data saved to {output_file}")
            
            # Save metrics
            metrics_file = output_file.replace('.csv', '_metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            self.logger.info(f"Metrics saved to {metrics_file}")
        
        return processed_df


def main():
    """CLI interface for patent processing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process patent data with AI classification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("input_file", help="Input CSV file with raw patent data")
    parser.add_argument("--output", "-o", 
                       default="processed_patents.csv",
                       help="Output CSV file for processed data")
    parser.add_argument("--include_abstracts", 
                       action="store_true",
                       help="Include patent abstracts in AI classification")
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file {args.input_file} not found")
        return 1
    
    # Process patents
    processor = PatentProcessor()
    df = processor.process_patents(
        input_file=args.input_file,
        output_file=args.output,
        include_abstracts=args.include_abstracts
    )
    
    print(f"✅ Processing complete: {len(df)} patents processed")
    print(f"📊 AI patents: {len(df[df['is_ai'] == True])} ({len(df[df['is_ai'] == True])/len(df)*100:.1f}%)")
    
    return 0


if __name__ == "__main__":
    exit(main())