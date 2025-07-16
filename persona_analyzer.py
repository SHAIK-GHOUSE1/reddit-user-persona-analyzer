import os
import praw
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime
from collections import Counter

# Load environment variables
load_dotenv()


class RedditPersonaAnalyzer:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )

    def get_user_info(self, username: str) -> Dict:
        """Fetch basic user information"""
        try:
            redditor = self.reddit.redditor(username)
            return {
                "name": redditor.name,
                "created_utc": redditor.created_utc,
                "comment_karma": redditor.comment_karma,
                "link_karma": redditor.link_karma,
                "is_gold": redditor.is_gold,
                "is_mod": redditor.is_mod,
            }
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return {}

    def get_user_content(self, username: str, limit: int = 100) -> Dict:
        """Fetch user posts and comments"""
        try:
            redditor = self.reddit.redditor(username)

            # Get recent comments
            comments = []
            for comment in redditor.comments.new(limit=limit):
                comments.append(
                    {
                        "id": comment.id,
                        "subreddit": str(comment.subreddit),
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": comment.created_utc,
                        "permalink": comment.permalink,
                    }
                )

            # Get recent submissions
            submissions = []
            for submission in redditor.submissions.new(limit=limit):
                submissions.append(
                    {
                        "id": submission.id,
                        "subreddit": str(submission.subreddit),
                        "title": submission.title,
                        "selftext": submission.selftext,
                        "score": submission.score,
                        "created_utc": submission.created_utc,
                        "permalink": submission.permalink,
                        "url": submission.url,
                    }
                )

            return {"comments": comments, "submissions": submissions}
        except Exception as e:
            print(f"Error fetching user content: {e}")
            return {"comments": [], "submissions": []}

    def analyze_persona(self, username: str) -> Dict:
        """Generate user persona based on Reddit activity"""
        user_info = self.get_user_info(username)
        content = self.get_user_content(username)

        persona = {
            "basic_info": user_info,
            "interests": self._extract_interests(content),
            "behavior": self._extract_behavior(content),
            "personality_traits": self._extract_personality(content),
            "potential_demographics": self._extract_demographics(content),
            "sources": content,  # Raw data for citations
        }

        return persona

    def _extract_interests(self, content: Dict) -> Dict:
        """Enhanced interest detection with subreddit analysis and keyword extraction"""
        subreddit_counts = {}
        keywords = []

        for comment in content["comments"]:
            sub = comment["subreddit"]
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
            keywords.extend(self._extract_keywords(comment["body"]))

        for submission in content["submissions"]:
            sub = submission["subreddit"]
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
            if submission["selftext"]:
                keywords.extend(self._extract_keywords(submission["selftext"]))
            keywords.extend(self._extract_keywords(submission["title"]))

        # Get top 5 subreddits
        sorted_subs = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "top_subreddits": [sub[0] for sub in sorted_subs[:5]],
            "common_keywords": self._get_most_common(keywords),
            "subreddit_counts": subreddit_counts,
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction"""
        STOP_WORDS = {"the", "and", "but", "are", "is", "i", "you", "me"}
        words = [word.lower() for word in text.split() if word.isalpha()]
        return [word for word in words if word not in STOP_WORDS and len(word) > 3]

    def _get_most_common(self, words: List[str], top_n: int = 10) -> List[str]:
        """Get most frequently occurring words"""
        return [word[0] for word in Counter(words).most_common(top_n)]

    def _extract_behavior(self, content: Dict) -> Dict:
        """Analyze user behavior patterns"""
        behavior = {
            "comment_length_avg": self._avg_comment_length(content["comments"]),
            "post_type_ratio": self._post_type_ratio(content),
            "active_times": self._extract_active_times(content),
            "engagement_level": self._calculate_engagement(content),
        }
        return behavior

    def _extract_personality(self, content: Dict) -> List[str]:
        """Extract personality traits from content"""
        traits = []
        positive_words = {"love", "great", "awesome", "happy", "nice"}
        negative_words = {"hate", "awful", "terrible", "bad", "angry"}

        positive_count = 0
        negative_count = 0

        for comment in content["comments"]:
            body = comment["body"].lower()
            positive_count += sum(1 for word in positive_words if word in body)
            negative_count += sum(1 for word in negative_words if word in body)

        if positive_count > negative_count * 1.5:
            traits.append("Positive")
        elif negative_count > positive_count * 1.5:
            traits.append("Negative")

        if self._avg_comment_length(content["comments"]) > 150:
            traits.append("Detailed/Thoughtful")
        elif self._avg_comment_length(content["comments"]) < 50:
            traits.append("Concise")

        return traits

    def _extract_demographics(self, content: Dict) -> Dict:
        """Infer potential demographics"""
        demographics = {}
        timezone_guess = self._guess_timezone(content)
        if timezone_guess:
            demographics["likely_timezone"] = timezone_guess

        # Simple language analysis for potential location
        us_indicators = {"america", "usa", "us", "united states"}
        uk_indicators = {"uk", "britain", "england", "london"}

        for comment in content["comments"]:
            text = comment["body"].lower()
            if any(word in text for word in us_indicators):
                demographics["possible_location"] = "United States"
                break
            elif any(word in text for word in uk_indicators):
                demographics["possible_location"] = "United Kingdom"
                break

        return demographics

    def _extract_active_times(self, content: Dict) -> Dict:
        """Extract when the user is most active"""
        hours = []
        for item in content["comments"] + content["submissions"]:
            dt = datetime.fromtimestamp(item["created_utc"])
            hours.append(dt.hour)

        if not hours:
            return {}

        hour_counts = Counter(hours)
        most_active = hour_counts.most_common(3)
        return {
            "most_active_hours": [f"{hour}:00-{hour+1}:00" for hour, _ in most_active],
            "activity_distribution": dict(hour_counts),
        }

    def _calculate_engagement(self, content: Dict) -> str:
        """Calculate user engagement level"""
        total_posts = len(content["comments"]) + len(content["submissions"])
        if total_posts == 0:
            return "Inactive"

        avg_score = (
            sum(item["score"] for item in content["comments"] + content["submissions"])
            / total_posts
        )

        if total_posts > 50 and avg_score > 10:
            return "Highly Engaged"
        elif total_posts > 20 or avg_score > 5:
            return "Active"
        else:
            return "Occasional"

    def _guess_timezone(self, content: Dict) -> Optional[str]:
        """Guess timezone based on posting times"""
        if not content["comments"] and not content["submissions"]:
            return None

        # Get all post/comment times
        times = [
            datetime.fromtimestamp(item["created_utc"]).hour
            for item in content["comments"] + content["submissions"]
        ]

        if not times:
            return None

        # Find most active hours
        active_hours = Counter(times).most_common(3)
        avg_active = sum(h for h, _ in active_hours) / len(active_hours)

        # Simple timezone estimation
        if 0 <= avg_active < 6:
            return "UTC-5 to UTC-8 (Americas night time)"
        elif 6 <= avg_active < 12:
            return "UTC+0 to UTC+5 (Europe morning)"
        elif 12 <= avg_active < 18:
            return "UTC+8 to UTC+10 (Asia afternoon)"
        else:
            return "UTC+1 to UTC+3 (Europe evening)"

    # Helper methods
    def _avg_comment_length(self, comments: List[Dict]) -> float:
        if not comments:
            return 0
        total = sum(len(c["body"]) for c in comments)
        return total / len(comments)

    def _post_type_ratio(self, content: Dict) -> Dict:
        total = len(content["comments"]) + len(content["submissions"])
        if total == 0:
            return {"comments": 0, "submissions": 0}
        return {
            "comments": len(content["comments"]) / total,
            "submissions": len(content["submissions"]) / total,
        }

    def save_persona(self, persona: Dict, filename: str):
        """Save complete persona analysis to file with citations"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                f"Reddit User Persona Analysis for {persona['basic_info'].get('name', 'N/A')}\n"
            )
            f.write("=" * 50 + "\n\n")

            # Basic info
            f.write("BASIC INFORMATION:\n")
            f.write(f"- Username: {persona['basic_info'].get('name', 'N/A')}\n")
            f.write(
                f"- Account created: {datetime.fromtimestamp(persona['basic_info'].get('created_utc', 0))}\n"
            )
            f.write(
                f"- Comment karma: {persona['basic_info'].get('comment_karma', 0)}\n"
            )
            f.write(f"- Post karma: {persona['basic_info'].get('link_karma', 0)}\n")
            f.write(
                f"- Premium: {'Yes' if persona['basic_info'].get('is_gold') else 'No'}\n"
            )
            f.write(
                f"- Moderator: {'Yes' if persona['basic_info'].get('is_mod') else 'No'}\n\n"
            )

            # Interests with citations
            f.write("INTERESTS:\n")
            if persona["interests"].get("top_subreddits"):
                f.write(
                    f"- Top subreddits: {', '.join(persona['interests']['top_subreddits'])}\n"
                )
                # Add citation example
                example_sub = persona["interests"]["top_subreddits"][0]
                example_post = next(
                    (
                        p
                        for p in persona["sources"]["submissions"]
                        if p["subreddit"] == example_sub
                    ),
                    None,
                )
                if example_post:
                    f.write(
                        f"  (Source: Post '{example_post['title'][:30]}...' in r/{example_sub})\n"
                    )

            if persona["interests"].get("common_keywords"):
                f.write(
                    f"- Common keywords: {', '.join(persona['interests']['common_keywords'])}\n"
                )
                # Add citation example
                keyword = persona["interests"]["common_keywords"][0]
                example_comment = next(
                    (
                        c
                        for c in persona["sources"]["comments"]
                        if keyword in c["body"].lower()
                    ),
                    None,
                )
                if example_comment:
                    f.write(
                        f"  (Source: Comment in r/{example_comment['subreddit']}: '{example_comment['body'][:30]}...')\n"
                    )
            f.write("\n")

            # Behavior
            f.write("BEHAVIOR PATTERNS:\n")
            f.write(
                f"- Average comment length: {persona['behavior'].get('comment_length_avg', 0):.1f} characters\n"
            )
            f.write(
                f"- Comment to post ratio: {persona['behavior'].get('post_type_ratio', {}).get('comments', 0)*100:.1f}% comments, "
                f"{persona['behavior'].get('post_type_ratio', {}).get('submissions', 0)*100:.1f}% submissions\n"
            )

            if persona["behavior"].get("active_times", {}).get("most_active_hours"):
                f.write(
                    f"- Most active hours: {', '.join(persona['behavior']['active_times']['most_active_hours'])}\n"
                )

            f.write(
                f"- Engagement level: {persona['behavior'].get('engagement_level', 'Unknown')}\n\n"
            )

            # Personality
            f.write("PERSONALITY TRAITS:\n")
            if persona["personality_traits"]:
                for trait in persona["personality_traits"]:
                    f.write(f"- {trait}\n")
            else:
                f.write("- Could not determine significant personality traits\n")
            f.write("\n")

            # Demographics
            f.write("POTENTIAL DEMOGRAPHICS:\n")
            if persona["potential_demographics"].get("likely_timezone"):
                f.write(
                    f"- Likely timezone: {persona['potential_demographics']['likely_timezone']}\n"
                )
            if persona["potential_demographics"].get("possible_location"):
                f.write(
                    f"- Possible location: {persona['potential_demographics']['possible_location']}\n"
                )
            if not persona["potential_demographics"]:
                f.write("- Could not infer demographics\n")
            f.write("\n")

            # Sources
            f.write("SOURCES:\n")
            f.write(
                f"- Analyzed {len(persona['sources']['comments'])} comments and {len(persona['sources']['submissions'])} submissions\n"
            )

            # Sample content
            if persona["sources"]["comments"]:
                f.write("\nSAMPLE COMMENT:\n")
                sample = persona["sources"]["comments"][0]
                f.write(f"From r/{sample['subreddit']} (Score: {sample['score']}):\n")
                f.write(
                    sample["body"][:200]
                    + ("..." if len(sample["body"]) > 200 else "")
                    + "\n"
                )
                f.write(f"Permalink: https://reddit.com{sample['permalink']}\n")

            if persona["sources"]["submissions"]:
                f.write("\nSAMPLE POST:\n")
                sample = persona["sources"]["submissions"][0]
                f.write(f"From r/{sample['subreddit']} (Score: {sample['score']}):\n")
                f.write(f"Title: {sample['title']}\n")
                if sample["selftext"]:
                    f.write(
                        sample["selftext"][:200]
                        + ("..." if len(sample["selftext"]) > 200 else "")
                        + "\n"
                    )
                f.write(f"Permalink: https://reddit.com{sample['permalink']}\n")


def main():
    analyzer = RedditPersonaAnalyzer()

    print("Reddit User Persona Analyzer")
    print("=" * 30)
    profile_url = input("Enter Reddit profile URL: ").strip()
    username = profile_url.split("/")[-1]

    print(f"\nAnalyzing u/{username}...")
    persona = analyzer.analyze_persona(username)

    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"persona_{username}_{timestamp}.txt"
    analyzer.save_persona(persona, filename)

    print(f"\nAnalysis complete! Saved to {filename}")
    print(
        f"Found {len(persona['sources']['comments'])} comments and {len(persona['sources']['submissions'])} posts"
    )


if __name__ == "__main__":
    main()
