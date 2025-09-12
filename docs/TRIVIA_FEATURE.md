# 🧠 Daily Trivia Feature

## Overview

The Daily Trivia feature adds an engaging trivia game to goobie-bot that tests users' knowledge of LA sports teams. Users can participate in daily trivia questions about Galaxy, Dodgers, Lakers, Rams, and Kings.

## Features

### 🎯 Daily Trivia Posts

- **Schedule**: Posted every day at 8 PM PT
- **Location**: Configurable channel via `TRIVIA_CHANNEL_ID` environment variable
- **Format**: Rich embed with team branding and clear instructions

### 🎮 Interactive Experience

- **Public Announcement**: Bot posts in designated channel with "Start Trivia" button
- **Private Sessions**: Each user gets their own private DM for trivia
- **Time Limit**: 30 seconds per question to prevent cheating
- **One Attempt**: Users can only play once per day

### 🏆 Scoring System

- **Base Points**:
  - Easy questions: 10 points
  - Medium questions: 20 points
  - Hard questions: 30 points
- **Bonuses**:
  - Speed bonus: +1-5 points for quick answers
  - Streak bonus: +10% for 3+ correct answers in a row
- **Tracking**: Total score, accuracy, current streak, best streak

### 📊 Leaderboards

- **Daily Rankings**: Top 10 players
- **Personal Stats**: Individual user statistics
- **Real-time Updates**: Scores update immediately after each question

## Commands

### `/trivia`

View the current leaderboard and your personal statistics.

### `/trivia-admin` (Admin Only)

- **Add Question**: Instructions for adding new questions
- **View Stats**: System statistics and question breakdown
- **Reset Daily**: Emergency reset for daily trivia (if needed)

## Configuration

### Environment Variables

```bash
# Optional: Channel ID for daily trivia posts
TRIVIA_CHANNEL_ID=123456789012345678
```

### Database

- **Type**: SQLite database (`trivia/data/trivia.db`)
- **Tables**:
  - `trivia_scores`: User statistics and scores
  - `trivia_questions`: Question database
  - `trivia_daily_posts`: Daily post tracking
  - `trivia_attempts`: User attempt history

## Question Management

### Adding Questions

Questions are stored in `trivia/data/questions.json` and loaded into the database on startup.

**Question Format:**

```json
{
	"question": "Your question here?",
	"correct_answer": "Correct Answer",
	"wrong_answers": ["Wrong 1", "Wrong 2", "Wrong 3"],
	"category": "galaxy|dodgers|lakers|rams|kings|general",
	"difficulty": "easy|medium|hard"
}
```

### Categories

- **galaxy**: LA Galaxy soccer questions
- **dodgers**: Los Angeles Dodgers baseball questions
- **lakers**: Los Angeles Lakers basketball questions
- **rams**: Los Angeles Rams football questions
- **kings**: LA Kings hockey questions
- **general**: General LA sports questions

### Difficulties

- **easy**: Basic knowledge questions
- **medium**: Intermediate knowledge questions
- **hard**: Advanced/expert level questions

## User Experience Flow

1. **8 PM PT**: Bot posts daily trivia announcement in designated channel
2. **User Clicks**: "Start Trivia" button (disabled if already played today)
3. **Private DM**: User receives question with 4 multiple choice options
4. **30 Second Timer**: Visual countdown with automatic timeout
5. **Immediate Feedback**: Correct/incorrect with explanation
6. **Score Update**: Points added to user's total score
7. **Results Summary**: Final score and leaderboard position

## Privacy & Anti-Cheating

- **Private Sessions**: All trivia happens in private DMs
- **Time Limits**: 30-second response time prevents googling
- **One Attempt**: Daily limit prevents multiple attempts
- **Question Randomization**: Questions are shuffled to prevent sharing answers

## Technical Implementation

### File Structure

```
trivia/
├── __init__.py          # Module initialization
├── database.py          # SQLite database operations
├── scheduler.py         # Daily posting scheduler
├── commands.py          # Slash commands
├── ui.py               # Discord UI components
└── data/
    ├── questions.json  # Initial question database
    └── trivia.db      # SQLite database
```

### Key Components

- **TriviaDatabase**: Handles all database operations
- **TriviaScheduler**: Manages daily posting at 8 PM PT
- **TriviaView**: Discord button interactions
- **PrivateTriviaSession**: Individual user trivia sessions
- **TriviaAnswerView**: Question answering interface

## Integration

The trivia feature integrates seamlessly with the existing goobie-bot architecture:

- **Scheduler**: Runs alongside weekly matches scheduler
- **Commands**: Added to bot's slash command tree
- **Configuration**: Uses existing config system
- **Logging**: Follows established logging patterns
- **Error Handling**: Consistent with bot's error handling

## Future Enhancements

- **Multiple Questions**: Daily trivia with 3-5 questions
- **Categories**: User-selectable question categories
- **Achievements**: Badges and milestones for users
- **Tournaments**: Special events with unique rewards
- **Question Types**: True/false, fill-in-the-blank questions
- **Team-specific**: Questions focused on specific LA teams

## Troubleshooting

### Common Issues

1. **No Trivia Posted**: Check `TRIVIA_CHANNEL_ID` environment variable
2. **Database Errors**: Ensure `trivia/data/` directory exists and is writable
3. **Button Not Working**: Restart bot to sync persistent views
4. **Questions Not Loading**: Check `trivia/data/questions.json` format

### Logs

Trivia operations are logged with the `trivia` logger. Check bot logs for:

- Daily post scheduling
- Database operations
- User interactions
- Error messages

## Support

For issues or questions about the trivia feature:

1. Check the bot logs for error messages
2. Verify environment variables are set correctly
3. Ensure database permissions are correct
4. Test with `/trivia-admin` command for system status
