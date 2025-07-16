# Reddit User Persona Analyzer

A Python script that analyzes Reddit users' activity to generate comprehensive personas with cited sources.

## Features
- Extracts user information from Reddit profiles
- Analyzes comments and posts for behavioral patterns
- Generates detailed user personas
- Provides citations for all findings
- Saves results as formatted text files

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/reddit-user-persona-analyzer.git
   cd reddit-user-persona-analyzer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with your Reddit API credentials:
   ```text
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT="script:reddit-persona-analyzer:v1.0 (by /u/your_reddit_username)"
   ```

## Usage

Run the analyzer:
```bash
python persona_analyzer.py
```

When prompted, enter a Reddit profile URL (e.g.):
```text
https://www.reddit.com/user/Hungry-Move-6603/
```

## Sample Outputs

Output files are automatically saved in the `samples/` directory with this format:
```text
samples/
├── persona_Hungry-Move-6603_20250715_123456.txt
└── persona_kojied_20250715_123457.txt
```

### Example Analysis 1: u/Hungry-Move-6603
```text
Reddit User Persona Analysis for Hungry-Move-6603
==================================================

BASIC INFORMATION:
- Username: Hungry-Move-6603
- Account created: 2021-04-06 02:17:18
- Comment karma: 21
- Post karma: 117

INTERESTS:
- Top subreddits: lucknow, nagpur, IndiaUnfilter
  (Source: Post 'Reading Cafe / Reader' Club?...' in r/lucknow)

BEHAVIOR PATTERNS:
- Average comment length: 114.4 characters
- Most active hours: 10:00-11:00, 0:00-1:00

[Truncated... Full analysis available in samples/persona_Hungry-Move-6603_*.txt]
```

### Example Analysis 2: u/kojied
```text
Reddit User Persona Analysis for kojied
======================================

BASIC INFORMATION:
- Username: kojied
- Account created: 2020-01-03 02:36:25
- Comment karma: 1823
- Post karma: 216

INTERESTS:
- Top subreddits: AskReddit, civ5, AskNYC
  (Source: Post 'H1B holders, what are your tho...' in r/AskReddit)

BEHAVIOR PATTERNS:
- Average comment length: 228.8 characters
- Most active hours: 21:00-22:00, 20:00-21:00

[Truncated... Full analysis available in samples/persona_kojied_*.txt]
```

## Implementation Details

- Uses PRAW for Reddit API interaction
- PEP-8 compliant Python code
- Proper error handling for various edge cases
- Clear citation of sources for all persona attributes
