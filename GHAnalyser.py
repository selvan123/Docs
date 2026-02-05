#!/usr/bin/env python3
"""
GitHub Repository Analyzer - Agentic AI Model
Fetches GitHub repository metadata and uses Ollama for intelligent analysis and recommendations.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import sys
from dataclasses import dataclass
import os
from dotenv import load_dotenv


# Predefined list of repositories to analyze
REPOSITORY_LIST = [
    "microsoft/vscode",
    "facebook/react",
    "microsoft/TypeScript",
    "nodejs/node",
    "python/cpython",
    "torvalds/linux",
    "microsoft/PowerToys",
    "openai/whisper",
    "tensorflow/tensorflow",
    "kubernetes/kubernetes"
]


@dataclass
class RepoMetadata:
    """Data structure for repository metadata"""
    name: str
    description: str
    language: str
    stars: int
    forks: int
    open_issues: int
    created_at: str
    updated_at: str
    pushed_at: str
    size: int
    license: Optional[str]
    topics: List[str]
    branches: List[Dict]
    recent_commits: List[Dict]
    pull_requests: List[Dict]
    issues: List[Dict]
    contributors: List[Dict]
    languages: Dict[str, int]
    releases: List[Dict]


class GitHubAnalyzer:
    """GitHub repository data fetcher and analyzer"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Repo-Analyzer'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
        
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def fetch_repo_data(self, owner: str, repo: str) -> RepoMetadata:
        """Fetch comprehensive repository metadata from GitHub API"""
        base_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        print(f"🔍 Fetching repository data for {owner}/{repo}...")
        
        # Basic repository info
        repo_data = self._make_request(base_url)
        
        # Fetch additional data in parallel-like manner
        branches = self._fetch_branches(owner, repo)
        commits = self._fetch_recent_commits(owner, repo)
        pull_requests = self._fetch_pull_requests(owner, repo)
        issues = self._fetch_issues(owner, repo)
        contributors = self._fetch_contributors(owner, repo)
        languages = self._fetch_languages(owner, repo)
        releases = self._fetch_releases(owner, repo)
        
        return RepoMetadata(
            name=repo_data['name'],
            description=repo_data.get('description', 'No description'),
            language=repo_data.get('language', 'Unknown'),
            stars=repo_data['stargazers_count'],
            forks=repo_data['forks_count'],
            open_issues=repo_data['open_issues_count'],
            created_at=repo_data['created_at'],
            updated_at=repo_data['updated_at'],
            pushed_at=repo_data['pushed_at'],
            size=repo_data['size'],
            license=repo_data['license']['name'] if repo_data.get('license') else None,
            topics=repo_data.get('topics', []),
            branches=branches,
            recent_commits=commits,
            pull_requests=pull_requests,
            issues=issues,
            contributors=contributors,
            languages=languages,
            releases=releases
        )
    
    def _make_request(self, url: str) -> Dict:
        """Make authenticated request to GitHub API"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching data from {url}: {e}")
            return {}
    
    def _fetch_branches(self, owner: str, repo: str) -> List[Dict]:
        """Fetch repository branches"""
        url = f"https://api.github.com/repos/{owner}/{repo}/branches"
        branches = self._make_request(url)
        return branches[:10] if isinstance(branches, list) else []
    
    def _fetch_recent_commits(self, owner: str, repo: str, count: int = 10) -> List[Dict]:
        """Fetch recent commits"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={count}"
        commits = self._make_request(url)
        return commits if isinstance(commits, list) else []
    
    def _fetch_pull_requests(self, owner: str, repo: str) -> List[Dict]:
        """Fetch recent pull requests"""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=10"
        prs = self._make_request(url)
        return prs if isinstance(prs, list) else []
    
    def _fetch_issues(self, owner: str, repo: str) -> List[Dict]:
        """Fetch recent issues"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?per_page=10"
        issues = self._make_request(url)
        return issues if isinstance(issues, list) else []
    
    def _fetch_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Fetch top contributors"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=10"
        contributors = self._make_request(url)
        return contributors if isinstance(contributors, list) else []
    
    def _fetch_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch repository languages"""
        url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        languages = self._make_request(url)
        return languages if isinstance(languages, dict) else {}
    
    def _fetch_releases(self, owner: str, repo: str) -> List[Dict]:
        """Fetch repository releases"""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=5"
        releases = self._make_request(url)
        return releases if isinstance(releases, list) else []


class OllamaAgent:
    """Ollama AI agent for repository analysis"""
    
    def __init__(self, model: str = "mistral", ollama_url: str = "http://localhost:11434/api/generate"):
        self.model = model
        self.ollama_url = ollama_url
    
    def analyze_repository(self, metadata: RepoMetadata) -> str:
        """Send repository metadata to Ollama for analysis"""
        
        # Create structured prompt with metadata
        prompt = self._create_analysis_prompt(metadata)
        
        print("🤖 Sending data to Ollama for analysis...")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2000
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response received')
            
        except requests.RequestException as e:
            return f"❌ Error communicating with Ollama: {e}"
    
    def _create_analysis_prompt(self, metadata: RepoMetadata) -> str:
        """Create comprehensive analysis prompt for Ollama"""
        
        # Calculate some metrics
        days_since_creation = (datetime.now() - datetime.fromisoformat(metadata.created_at.replace('Z', '+00:00'))).days
        days_since_update = (datetime.now() - datetime.fromisoformat(metadata.updated_at.replace('Z', '+00:00'))).days
        
        # Build language distribution
        total_bytes = sum(metadata.languages.values())
        lang_percentages = {lang: round((bytes_count/total_bytes)*100, 1) 
                          for lang, bytes_count in metadata.languages.items()} if total_bytes > 0 else {}
        
        prompt = f"""
You are a senior software engineer and project manager. Analyze this GitHub repository and provide comprehensive insights and recommendations.

REPOSITORY OVERVIEW:
- Name: {metadata.name}
- Description: {metadata.description}
- Primary Language: {metadata.language}
- Stars: {metadata.stars:,} | Forks: {metadata.forks:,} | Open Issues: {metadata.open_issues}
- Size: {metadata.size:,} KB
- License: {metadata.license or 'None specified'}
- Topics: {', '.join(metadata.topics) if metadata.topics else 'None'}
- Created: {days_since_creation} days ago
- Last Updated: {days_since_update} days ago

ACTIVITY METRICS:
- Total Branches: {len(metadata.branches)}
- Recent Commits: {len(metadata.recent_commits)}
- Pull Requests: {len(metadata.pull_requests)}
- Active Issues: {len(metadata.issues)}
- Contributors: {len(metadata.contributors)}
- Releases: {len(metadata.releases)}

LANGUAGE COMPOSITION:
{json.dumps(lang_percentages, indent=2) if lang_percentages else 'No language data available'}

RECENT ACTIVITY SUMMARY:
Commits (last 10):
{self._format_commits(metadata.recent_commits[:5])}

Pull Requests:
{self._format_pull_requests(metadata.pull_requests[:5])}

Issues:
{self._format_issues(metadata.issues[:5])}

ANALYSIS REQUIREMENTS:
Please provide a comprehensive analysis covering:

1. **HEALTH ASSESSMENT**: Overall repository health, activity level, and maintenance status
2. **CODE QUALITY INDICATORS**: Based on structure, language choices, and patterns observed
3. **COMMUNITY ENGAGEMENT**: Contributor activity, issue resolution, PR patterns
4. **DEVELOPMENT PRACTICES**: Release management, branching strategy, documentation
5. **SECURITY & COMPLIANCE**: License, dependencies, security considerations
6. **GROWTH TRAJECTORY**: Star/fork trends, contributor growth, activity patterns
7. **ACTIONABLE RECOMMENDATIONS**: 
   - Immediate improvements needed
   - Long-term strategic suggestions
   - Community engagement opportunities
   - Technical debt indicators
   - Security enhancements

Provide specific, actionable insights backed by the data. Use emojis and clear formatting for readability.
"""
        
        return prompt
    
    def _format_commits(self, commits: List[Dict]) -> str:
        """Format commits for prompt"""
        if not commits:
            return "No recent commits found"
        
        formatted = []
        for commit in commits:
            author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
            message = commit.get('commit', {}).get('message', 'No message')[:60]
            date = commit.get('commit', {}).get('author', {}).get('date', 'Unknown date')
            formatted.append(f"  • {message}... by {author} ({date[:10]})")
        
        return '\n'.join(formatted)
    
    def _format_pull_requests(self, prs: List[Dict]) -> str:
        """Format pull requests for prompt"""
        if not prs:
            return "No pull requests found"
        
        formatted = []
        for pr in prs:
            title = pr.get('title', 'No title')[:50]
            state = pr.get('state', 'unknown')
            user = pr.get('user', {}).get('login', 'Unknown')
            formatted.append(f"  • [{state.upper()}] {title}... by {user}")
        
        return '\n'.join(formatted)
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format issues for prompt"""
        if not issues:
            return "No issues found"
        
        formatted = []
        for issue in issues:
            if 'pull_request' in issue:  # Skip PRs in issues endpoint
                continue
            title = issue.get('title', 'No title')[:50]
            state = issue.get('state', 'unknown')
            labels = [label['name'] for label in issue.get('labels', [])]
            label_str = f" [{', '.join(labels[:2])}]" if labels else ""
            formatted.append(f"  • [{state.upper()}] {title}...{label_str}")
        
        return '\n'.join(formatted) if formatted else "No issues found"


def main():
    """Main execution function"""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='GitHub Repository Analyzer with Ollama AI')
    parser.add_argument('repository', nargs='?', help='Repository in format owner/repo (optional if using --batch)')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--model', default='mistral', help='Ollama model to use (default: mistral)')
    parser.add_argument('--ollama-url', default='http://localhost:11434/api/generate', 
                       help='Ollama API URL')
    parser.add_argument('--batch', action='store_true', 
                       help='Analyze all repositories in the predefined list')
    parser.add_argument('--list', action='store_true', 
                       help='Show the predefined repository list')
    
    args = parser.parse_args()
    
    # Show repository list if requested
    if args.list:
        print("📋 Predefined Repository List:")
        print("=" * 40)
        for i, repo in enumerate(REPOSITORY_LIST, 1):
            print(f"{i:2d}. {repo}")
        return
    
    # Determine which repositories to analyze
    if args.batch:
        repositories = REPOSITORY_LIST
        print(f"🔄 Batch mode: Analyzing {len(repositories)} repositories")
    elif args.repository:
        repositories = [args.repository]
    else:
        # Default to batch mode when no parameters provided
        repositories = REPOSITORY_LIST
        print(f"🔄 Default batch mode: Analyzing {len(repositories)} repositories")
        print("💡 Use --list to see repositories or specify owner/repo for single analysis")
    
    # Get GitHub token from environment if not provided
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("⚠️  No GitHub token provided. API rate limits will be lower.")
        print("💡 Set GITHUB_TOKEN in .env file or use --token flag")
    
    # Initialize analyzer and agent
    analyzer = GitHubAnalyzer(token)
    agent = OllamaAgent(args.model, args.ollama_url)
    
    try:
        for i, repo_name in enumerate(repositories, 1):
            # Parse repository
            try:
                owner, repo = repo_name.split('/')
            except ValueError:
                print(f"❌ Invalid repository format: {repo_name} (should be 'owner/repo')")
                continue
            
            print("\n" + "=" * 80)
            if len(repositories) > 1:
                print(f"📊 Analysis {i}/{len(repositories)}: {repo_name}")
            else:
                print(f"📊 GitHub Repository Analysis: {repo_name}")
            print("=" * 80)
            
            # Fetch repository data
            metadata = analyzer.fetch_repo_data(owner, repo)
            
            if not metadata.name:  # Check if data was fetched successfully
                print(f"❌ Failed to fetch data for {repo_name}")
                continue
            
            # Get AI analysis
            print("\n" + "=" * 60)
            print("🤖 AI Analysis and Recommendations")
            print("=" * 60)
            
            analysis = agent.analyze_repository(metadata)
            print(analysis)
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{owner}_{repo}_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# GitHub Repository Analysis: {repo_name}\n\n")
                f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Repository Overview\n\n")
                f.write(f"- **Name:** {metadata.name}\n")
                f.write(f"- **Description:** {metadata.description}\n")
                f.write(f"- **Language:** {metadata.language}\n")
                f.write(f"- **Stars:** {metadata.stars:,}\n")
                f.write(f"- **Forks:** {metadata.forks:,}\n")
                f.write(f"- **Open Issues:** {metadata.open_issues}\n")
                f.write(f"- **License:** {metadata.license or 'None specified'}\n\n")
                f.write("## AI Analysis and Recommendations\n\n")
                f.write(analysis)
            
            print(f"\n💾 Analysis saved to: {filename}")
            
            # Add delay between analyses in batch mode to respect API limits
            if len(repositories) > 1 and i < len(repositories):
                print("\n⏳ Waiting 10 seconds before next analysis...")
                import time
                time.sleep(10)
        
        if len(repositories) > 1:
            print(f"\n✅ Completed batch analysis of {len(repositories)} repositories!")
            
    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
