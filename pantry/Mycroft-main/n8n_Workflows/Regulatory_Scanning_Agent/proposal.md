# Regulatory Risk Scanner - Project Concept

## Overview

An automated monitoring system that tracks AI-related regulatory developments from free public sources, analyzes their potential impact, and alerts on significant changes affecting investment positions.

## Core Problem

Regulatory changes affecting AI companies are scattered across government sites, legal publications, and news sources. Important policy shifts often appear in technical documents before reaching mainstream financial coverage. This creates an information gap where regulatory risks aren't identified until markets have already reacted.

## Solution Approach

The system runs scheduled checks against curated government and news sources, collecting new regulatory announcements. Each item gets analyzed by a local language model to extract key attributes and assess impact. High-priority developments trigger alerts, while everything gets logged for historical tracking and pattern analysis.

## Key Components

### Data Collection
Monitor regulatory and news sources using RSS feeds and public APIs. All sources use free tiers or publicly available data.

**Sources include:**
- Government agencies (Federal Register, SEC, EU Commission)
- News aggregators (NewsAPI, Google News, Bing News)
- Legal analysis sites (JDSupra, Lexology)

### Analysis Engine
Run a local language model to analyze each regulatory item without API costs. The model extracts structured information to make items searchable and actionable.

**Analysis outputs:**
- Severity classification (1-5 scale)
- Affected subsectors (semiconductors, cloud, models, applications)
- Geographic scope (US, EU, China, etc.)
- Timeline (immediate, 6-month, 12-month+)
- Investment impact assessment (bullish/bearish/neutral)

### Storage and Tracking
Store analyzed items in a structured database that enables historical review and pattern identification.

**Key fields:**
- Date, title, source
- Severity, subsectors, geography
- Summary and full content
- Review status (new/reviewed/actioned)

### Alert Logic
Send notifications only for genuinely significant developments to avoid alert fatigue. Lower-priority items accumulate for periodic review.

**Alert triggers:**
- Severity above configured threshold (e.g., ≥3)
- Multiple portfolio holdings affected
- Immediate implementation timeline


