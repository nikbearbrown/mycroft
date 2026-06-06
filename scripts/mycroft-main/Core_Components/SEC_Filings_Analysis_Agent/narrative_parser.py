#!/usr/bin/env python3
"""
Enhanced SEC Narrative Parser for n8n Integration
Extracts and analyzes narrative content from SEC filings with improved insights.
"""

import os
import re
import json
import sys
import argparse
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime

class EnhancedNarrativeParser:
    """Enhanced SEC filing narrative parser with better analysis capabilities."""
    
    def __init__(self):
        # Keywords for different business themes
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'ai technology', 'neural network',
            'deep learning', 'natural language', 'computer vision', 'automation',
            'algorithm', 'predictive analytics', 'data science', 'chatbot', 'generative ai'
        ]
        
        self.risk_keywords = [
            'risk', 'uncertainty', 'challenge', 'threat', 'competition', 'regulatory',
            'litigation', 'cybersecurity', 'data breach', 'compliance', 'volatile'
        ]
        
        self.growth_keywords = [
            'growth', 'expansion', 'opportunity', 'investment', 'innovation', 'strategic',
            'acquisition', 'development', 'market penetration', 'revenue growth'
        ]
    
    def parse_filing_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a single filing file and extract enhanced narrative blocks.
        
        Returns list of narrative blocks with metadata.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '<html' in content.lower() or '<div' in content.lower():
                return self._parse_html_content(content)
            else:
                return self._parse_text_content(content)
                
        except Exception as e:
            return [{'error': f"Error parsing {file_path}: {e}"}]
    
    def _parse_html_content(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract and analyze narrative blocks from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'meta', 'link', 'head', 'table']):
            element.decompose()
        
        # Find substantial text blocks
        text_elements = soup.find_all(['div', 'p', 'td', 'span', 'section'])
        narrative_blocks = []
        
        for element in text_elements:
            text = element.get_text(strip=True)
            
            # Filter for substantial narrative content
            if self._is_narrative_content(text):
                cleaned_text = self._clean_text(text)
                
                # Analyze the block
                analysis = self._analyze_text_block(cleaned_text)
                
                block_data = {
                    'text': cleaned_text,
                    'char_count': len(cleaned_text),
                    'word_count': len(cleaned_text.split()),
                    'analysis': analysis
                }
                narrative_blocks.append(block_data)
        
        # Remove duplicates and sort by relevance
        unique_blocks = self._remove_duplicate_blocks(narrative_blocks)
        unique_blocks.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
        
        return unique_blocks[:20]  # Return top 20 blocks
    
    def _parse_text_content(self, text_content: str) -> List[Dict[str, Any]]:
        """Extract and analyze narrative blocks from plain text."""
        sections = re.split(r'\n\s*\n', text_content)
        narrative_blocks = []
        
        for section in sections:
            cleaned = self._clean_text(section)
            
            if self._is_narrative_content(cleaned):
                analysis = self._analyze_text_block(cleaned)
                
                block_data = {
                    'text': cleaned,
                    'char_count': len(cleaned),
                    'word_count': len(cleaned.split()),
                    'analysis': analysis
                }
                narrative_blocks.append(block_data)
        
        unique_blocks = self._remove_duplicate_blocks(narrative_blocks)
        unique_blocks.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
        
        return unique_blocks[:20]
    
    def _is_narrative_content(self, text: str) -> bool:
        """Enhanced check for narrative content."""
        if len(text) < 500:  # Minimum length for narrative
            return False
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return False
        
        # Check for navigation/TOC patterns
        short_lines = sum(1 for line in lines if len(line) < 80)
        short_ratio = short_lines / len(lines) if lines else 1
        
        # TOC indicators
        toc_patterns = [
            r'table of contents',
            r'page \d+',
            r'\.{3,}',  # Multiple dots
            r'^item \d+',  # SEC item headers
            r'^\d+\.\d+',  # Numbered sections
        ]
        
        toc_matches = sum(1 for line in lines for pattern in toc_patterns 
                         if re.search(pattern, line.lower()))
        toc_ratio = toc_matches / len(lines) if lines else 0
        
        # Narrative indicators
        sentence_count = len(re.findall(r'[.!?]+', text))
        avg_sentence_length = len(text.split()) / max(sentence_count, 1)
        
        # Rules for narrative content
        is_narrative = (
            short_ratio < 0.5 and  # Not mostly short lines
            toc_ratio < 0.2 and    # Not table of contents
            avg_sentence_length > 8 and  # Reasonable sentence length
            sentence_count > 5     # Multiple sentences
        )
        
        return is_narrative
    
    def _analyze_text_block(self, text: str) -> Dict[str, Any]:
        """Analyze a text block for themes and relevance."""
        text_lower = text.lower()
        
        # Count keyword mentions
        ai_mentions = sum(1 for keyword in self.ai_keywords if keyword in text_lower)
        risk_mentions = sum(1 for keyword in self.risk_keywords if keyword in text_lower)
        growth_mentions = sum(1 for keyword in self.growth_keywords if keyword in text_lower)
        
        # Calculate theme scores
        total_words = len(text.split())
        ai_density = (ai_mentions / total_words) * 1000 if total_words > 0 else 0
        risk_density = (risk_mentions / total_words) * 1000 if total_words > 0 else 0
        growth_density = (growth_mentions / total_words) * 1000 if total_words > 0 else 0
        
        # Determine primary theme
        theme_scores = {
            'ai_technology': ai_density,
            'risk_factors': risk_density,
            'growth_strategy': growth_density
        }
        primary_theme = max(theme_scores.keys(), key=lambda k: theme_scores[k])
        
        # Calculate relevance score
        relevance_score = ai_mentions * 3 + risk_mentions * 2 + growth_mentions * 2
        
        # Extract key sentences (those with important keywords)
        key_sentences = self._extract_key_sentences(text)
        
        return {
            'primary_theme': primary_theme,
            'theme_scores': theme_scores,
            'keyword_counts': {
                'ai_mentions': ai_mentions,
                'risk_mentions': risk_mentions,
                'growth_mentions': growth_mentions
            },
            'relevance_score': relevance_score,
            'key_sentences': key_sentences[:3],  # Top 3 key sentences
            'readability_score': self._calculate_readability(text)
        }
    
    def _extract_key_sentences(self, text: str) -> List[str]:
        """Extract sentences containing important keywords."""
        sentences = re.split(r'[.!?]+', text)
        key_sentences = []
        
        all_keywords = self.ai_keywords + self.risk_keywords + self.growth_keywords
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50:  # Minimum sentence length
                keyword_count = sum(1 for keyword in all_keywords 
                                  if keyword in sentence.lower())
                if keyword_count > 0:
                    key_sentences.append({
                        'text': sentence,
                        'keyword_count': keyword_count
                    })
        
        # Sort by keyword density
        key_sentences.sort(key=lambda x: x['keyword_count'], reverse=True)
        return [s['text'] for s in key_sentences]
    
    def _calculate_readability(self, text: str) -> float:
        """Simple readability score (Flesch-Kincaid grade level approximation)."""
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        syllables = self._count_syllables(text)
        
        if sentences == 0 or words == 0:
            return 0
        
        # Simplified Flesch-Kincaid formula
        grade_level = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        return max(0, grade_level)
    
    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count."""
        # Simple syllable counting heuristic
        vowels = 'aeiouy'
        text = text.lower()
        syllables = 0
        prev_was_vowel = False
        
        for char in text:
            if char in vowels:
                if not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        return max(1, syllables)
    
    def _clean_text(self, text: str) -> str:
        """Enhanced text cleaning."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{3,}', '', text)
        text = re.sub(r'-{3,}', '', text)
        
        # Remove page numbers and references
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text)  # Trailing numbers
        
        # Fix spacing around punctuation
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def _remove_duplicate_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate blocks using similarity detection."""
        unique_blocks = []
        
        for block in blocks:
            is_duplicate = False
            block_text = block['text']
            
            for existing in unique_blocks:
                existing_text = existing['text']
                
                # Check for containment
                if len(block_text) < len(existing_text):
                    if block_text in existing_text:
                        is_duplicate = True
                        break
                else:
                    if existing_text in block_text:
                        # Replace existing with longer version
                        unique_blocks.remove(existing)
                        break
            
            if not is_duplicate:
                unique_blocks.append(block)
        
        return unique_blocks
    
    def parse_filing_directory(self, input_dir: str, output_dir: str, ticker: str) -> Dict[str, Any]:
        """
        Parse all filings in directory and create comprehensive analysis.
        
        Returns standardized JSON for n8n workflow.
        """
        try:
            if not os.path.exists(input_dir):
                raise Exception(f"Input directory {input_dir} does not exist")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Find 10-K files
            filing_files = [f for f in os.listdir(input_dir) 
                           if f.endswith(('.txt', '.html')) and '10-K' in f.upper()]
            
            if not filing_files:
                raise Exception(f"No 10-K filing files found in {input_dir}")
            
            all_blocks = []
            parsed_files = []
            
            for filename in filing_files:
                file_path = os.path.join(input_dir, filename)
                blocks = self.parse_filing_file(file_path)
                
                if blocks and 'error' not in blocks[0]:
                    all_blocks.extend(blocks)
                    
                    file_analysis = {
                        'filename': filename,
                        'blocks_count': len(blocks),
                        'total_characters': sum(b['char_count'] for b in blocks),
                        'primary_themes': self._get_file_themes(blocks)
                    }
                    parsed_files.append(file_analysis)
            
            # Generate comprehensive analysis
            comprehensive_analysis = self._generate_comprehensive_analysis(all_blocks, ticker)
            
            # Save detailed results
            output_file = os.path.join(output_dir, f"{ticker}_narrative_analysis.json")
            detailed_results = {
                'ticker': ticker,
                'analysis_timestamp': datetime.now().isoformat(),
                'files_parsed': parsed_files,
                'comprehensive_analysis': comprehensive_analysis,
                'all_narrative_blocks': all_blocks
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, indent=2, default=str)
            
            # Return summary for n8n
            return {
                'success': True,
                'ticker': ticker,
                'output_file': output_file,
                'summary': {
                    'files_processed': len(parsed_files),
                    'total_narrative_blocks': len(all_blocks),
                    'total_characters': sum(b['char_count'] for b in all_blocks),
                    'ai_focused_blocks': len([b for b in all_blocks 
                                            if b['analysis']['primary_theme'] == 'ai_technology']),
                    'key_themes': comprehensive_analysis['top_themes'],
                    'ai_readiness_score': comprehensive_analysis['ai_readiness_score']
                },
                'insights': comprehensive_analysis['key_insights']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ticker': ticker
            }
    
    def _get_file_themes(self, blocks: List[Dict[str, Any]]) -> List[str]:
        """Get primary themes for a file based on its blocks."""
        theme_counts = Counter()
        
        for block in blocks:
            theme = block['analysis']['primary_theme']
            score = block['analysis']['relevance_score']
            theme_counts[theme] += score
        
        return [theme for theme, count in theme_counts.most_common(3)]
    
    def _generate_comprehensive_analysis(self, all_blocks: List[Dict[str, Any]], ticker: str) -> Dict[str, Any]:
        """Generate comprehensive analysis across all narrative blocks."""
        if not all_blocks:
            return {'error': 'No blocks to analyze'}
        
        # Calculate AI readiness score
        ai_blocks = [b for b in all_blocks if b['analysis']['primary_theme'] == 'ai_technology']
        ai_readiness_score = min(100, len(ai_blocks) * 10 + sum(b['analysis']['relevance_score'] for b in ai_blocks))
        
        # Theme distribution
        themes = [b['analysis']['primary_theme'] for b in all_blocks]
        theme_distribution = dict(Counter(themes))
        
        # Extract top insights
        high_relevance_blocks = [b for b in all_blocks if b['analysis']['relevance_score'] > 5]
        
        # Generate key insights
        insights = []
        
        if ai_blocks:
            ai_char_count = sum(b['char_count'] for b in ai_blocks)
            insights.append(f"AI/Technology mentions found in {len(ai_blocks)} narrative blocks ({ai_char_count:,} characters)")
            
            # Extract AI-specific insights
            ai_sentences = []
            for block in ai_blocks[:3]:  # Top 3 AI blocks
                ai_sentences.extend(block['analysis']['key_sentences'][:2])
            
            if ai_sentences:
                insights.append(f"Key AI focus areas identified in recent filings")
        
        # Risk analysis
        risk_blocks = [b for b in all_blocks if b['analysis']['primary_theme'] == 'risk_factors']
        if risk_blocks:
            insights.append(f"Risk factors discussed in {len(risk_blocks)} sections")
        
        # Growth analysis  
        growth_blocks = [b for b in all_blocks if b['analysis']['primary_theme'] == 'growth_strategy']
        if growth_blocks:
            insights.append(f"Growth strategies outlined in {len(growth_blocks)} sections")
        
        # Overall narrative complexity
        avg_readability = sum(b['analysis']['readability_score'] for b in all_blocks) / len(all_blocks)
        insights.append(f"Average content complexity: Grade level {avg_readability:.1f}")
        
        return {
            'ai_readiness_score': ai_readiness_score,
            'theme_distribution': theme_distribution,
            'top_themes': list(dict(Counter(themes).most_common(5)).keys()),
            'total_narrative_chars': sum(b['char_count'] for b in all_blocks),
            'high_relevance_blocks': len(high_relevance_blocks),
            'average_readability': avg_readability,
            'key_insights': insights,
            'ai_specific_analysis': {
                'ai_blocks_count': len(ai_blocks),
                'ai_content_chars': sum(b['char_count'] for b in ai_blocks),
                'top_ai_sentences': [b['analysis']['key_sentences'][0] 
                                   for b in ai_blocks[:3] 
                                   if b['analysis']['key_sentences']]
            }
        }

def main():
    """Command line interface for n8n integration."""
    parser = argparse.ArgumentParser(description='Enhanced SEC Narrative Parser for n8n')
    parser.add_argument('--input-dir', required=True, help='Directory with downloaded filings')
    parser.add_argument('--output-dir', required=True, help='Output directory for parsed content')
    parser.add_argument('--ticker', required=True, help='Stock ticker symbol')
    
    args = parser.parse_args()
    
    try:
        narrative_parser = EnhancedNarrativeParser()
        result = narrative_parser.parse_filing_directory(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            ticker=args.ticker
        )
        
        # Output JSON for n8n
        print(json.dumps(result, default=str))
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'ticker': args.ticker
        }
        print(json.dumps(error_output))
        sys.exit(1)

if __name__ == "__main__":
    main()