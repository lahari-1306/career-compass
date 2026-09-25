# -*- coding: utf-8 -*-
"""
Enriches data/learning_resources.json with verified learning resources for
Web Development, Reasoning, Skill Development, AI/Data Science, and Interview Preparation.
Preserves all 24 existing resources exactly as they are.
"""

import json
import os
import sqlite3

ADDITIONAL_RESOURCES = [
    {
        "id": "res-mdn",
        "name": "MDN Web Docs",
        "description": "The premier open documentation and learning resource by Mozilla, covering HTML5, CSS Grid/Flexbox, JavaScript ES6+, Web APIs, and web accessibility standards.",
        "official_url": "https://developer.mozilla.org",
        "logo_url": "https://developer.mozilla.org/favicon-48x48.png",
        "category": "Web Development",
        "resource_type": "Official Documentation",
        "education_levels": ["B.Tech", "Degree", "Diploma", "Intermediate", "All"],
        "streams": ["Computer Science", "Information Technology", "All Streams"],
        "branches": ["CSE", "IT", "All Branches"],
        "skills": ["HTML5", "CSS3", "JavaScript", "Web APIs", "Frontend Development"],
        "exams": ["Campus Placements", "Technical Interviews"],
        "access_type": "OFFICIAL FREE RESOURCE",
        "free_features": ["Complete open web documentation", "Interactive examples", "Web technology references"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://developer.mozilla.org",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-freecodecamp",
        "name": "freeCodeCamp",
        "description": "Donor-supported non-profit educational platform offering structured, interactive certifications in Responsive Web Design, JavaScript Algorithms, and Front End Development.",
        "official_url": "https://www.freecodecamp.org",
        "logo_url": "https://www.freecodecamp.org/favicon-32x32.png",
        "category": "Web Development",
        "resource_type": "Learning Platform",
        "education_levels": ["B.Tech", "Degree", "Diploma", "Intermediate", "All"],
        "streams": ["Computer Science", "Information Technology", "All Streams"],
        "branches": ["CSE", "IT", "All Branches"],
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "exams": ["Campus Placements", "Full Stack Certifications"],
        "access_type": "OFFICIAL FREE RESOURCE",
        "free_features": ["Full curriculum free", "Interactive coding challenges", "Verified project certifications"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://www.freecodecamp.org",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-indiabix-reasoning",
        "name": "IndiaBIX Reasoning & Analytical Practice",
        "description": "Comprehensive practice bank for verbal and non-verbal logical reasoning, syllogisms, blood relations, seating arrangements, and direction sense.",
        "official_url": "https://www.indiabix.com/logical-reasoning/questions-and-answers/",
        "logo_url": "https://www.indiabix.com/favicon.ico",
        "category": "Reasoning",
        "resource_type": "Practice & Assessment Portal",
        "education_levels": ["B.Tech", "Degree", "Diploma", "Intermediate", "All"],
        "streams": ["All Streams"],
        "branches": ["All Branches"],
        "skills": ["Logical Reasoning", "Analytical Deduction", "Syllogisms", "Seating Arrangement", "Puzzles"],
        "exams": ["TCS NQT", "Infosys", "Cognizant", "Wipro", "SSC", "Banking"],
        "access_type": "FREE",
        "free_features": ["Unlimited reasoning MCQs", "Step-by-step explanations", "Topic-wise practice sets"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://www.indiabix.com",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-google-mlcc",
        "name": "Google Machine Learning Crash Course",
        "description": "Fast-paced, practical introduction to machine learning featuring video lectures from Google researchers, interactive visualizations, and TensorFlow/scikit-learn coding exercises.",
        "official_url": "https://developers.google.com/machine-learning/crash-course",
        "logo_url": "https://www.gstatic.com/devrel-devsite/prod/v22d25039f/developers/images/favicon.png",
        "category": "AI, ML & Data Science",
        "resource_type": "Official Educational Portal",
        "education_levels": ["B.Tech", "Degree", "Postgraduate", "All"],
        "streams": ["Computer Science", "Data Science", "All Engineering"],
        "branches": ["CSE", "AI/ML", "Data Science", "All Branches"],
        "skills": ["Machine Learning", "TensorFlow", "Regression", "Neural Networks", "Data Preparation"],
        "exams": ["Campus Placements", "Data Science Interviews"],
        "access_type": "OFFICIAL FREE RESOURCE",
        "free_features": ["25+ interactive lessons", "Real-world case studies", "Interactive Colab notebooks"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://developers.google.com",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-github-skills",
        "name": "GitHub Skills",
        "description": "Interactive GitHub-hosted learning laboratory teaching Git version control, branching, resolving merge conflicts, and automated GitHub Actions workflows.",
        "official_url": "https://skills.github.com/",
        "logo_url": "https://github.githubassets.com/favicons/favicon.png",
        "category": "Skill Development",
        "resource_type": "Interactive Learning Platform",
        "education_levels": ["B.Tech", "Degree", "Diploma", "Postgraduate", "All"],
        "streams": ["Computer Science", "Information Technology", "All Streams"],
        "branches": ["CSE", "ECE", "All Branches"],
        "skills": ["Git", "GitHub", "Version Control", "Pull Requests", "CI/CD"],
        "exams": ["Campus Placements", "Software Engineering Interviews"],
        "access_type": "OFFICIAL FREE RESOURCE",
        "free_features": ["Interactive repository-based courses", "Automated bot feedback", "Free certification badges"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://skills.github.com",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-linux-journey",
        "name": "Linux Journey",
        "description": "Free, beautifully organized web guide teaching Linux command-line essentials, filesystem hierarchies, file permissions, shell scripting, and process management.",
        "official_url": "https://linuxjourney.com/",
        "logo_url": "https://linuxjourney.com/favicon.ico",
        "category": "Skill Development",
        "resource_type": "Interactive Guide",
        "education_levels": ["B.Tech", "Degree", "Diploma", "Postgraduate", "All"],
        "streams": ["Computer Science", "Information Technology", "All Streams"],
        "branches": ["CSE", "IT", "ECE", "All Branches"],
        "skills": ["Linux", "Bash", "Shell Scripting", "CLI", "File Permissions"],
        "exams": ["DevOps Interviews", "Technical Rounds"],
        "access_type": "FREE",
        "free_features": ["Full course modules", "Command exercises", "Self-assessments"],
        "paid_features": "",
        "language": "English",
        "official_source": "https://linuxjourney.com",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    },
    {
        "id": "res-interviewbit",
        "name": "InterviewBit",
        "description": "Structured technical interview prep platform featuring company-tagged algorithmic problem tracks, system design tutorials, and timed mock coding assessments.",
        "official_url": "https://www.interviewbit.com/practice/",
        "logo_url": "https://www.interviewbit.com/favicon.ico",
        "category": "Interview Preparation",
        "resource_type": "Interview Preparation Platform",
        "education_levels": ["B.Tech", "Degree", "Postgraduate", "All"],
        "streams": ["Computer Science", "Engineering", "All Streams"],
        "branches": ["CSE", "IT", "ECE", "All Branches"],
        "skills": ["Algorithms", "Data Structures", "System Design", "Mock Interviews"],
        "exams": ["Campus Placements", "Product Company Interviews"],
        "access_type": "FREE + PAID",
        "free_features": ["Topic-wise practice questions", "Company-specific tracks", "Solution discussions"],
        "paid_features": "Premium mock interviews and mentorship bootcamps",
        "language": "English",
        "official_source": "https://www.interviewbit.com",
        "verification_status": "VERIFIED",
        "last_verified": "2026-09-25",
        "created_at": "2026-09-25T12:00:00+05:30",
        "updated_at": "2026-09-25T12:00:00+05:30"
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "learning_resources.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
        
    existing_ids = {r["id"] for r in existing}
    added_count = 0
    
    for new_r in ADDITIONAL_RESOURCES:
        if new_r["id"] not in existing_ids:
            existing.append(new_r)
            existing_ids.add(new_r["id"])
            added_count += 1
            
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
        
    print(f"Added {added_count} new resources to {json_path}. Total: {len(existing)}")
    
    # Also update SQLite database if exists
    db_path = os.path.join(base_dir, "data", "career_compass.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for r in ADDITIONAL_RESOURCES:
            cursor.execute("""
            INSERT OR REPLACE INTO learning_resources (
                id, name, description, official_url, logo_url, category, resource_type,
                education_levels, streams, branches, skills, exams, access_type,
                free_features, paid_features, language, official_source,
                verification_status, last_verified, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("id"),
                r.get("name"),
                r.get("description"),
                r.get("official_url"),
                r.get("logo_url", ""),
                r.get("category", "General"),
                r.get("resource_type", "Practice & Learning Platform"),
                json.dumps(r.get("education_levels", [])),
                json.dumps(r.get("streams", [])),
                json.dumps(r.get("branches", [])),
                json.dumps(r.get("skills", [])),
                json.dumps(r.get("exams", [])),
                r.get("access_type", "FREE"),
                json.dumps(r.get("free_features", [])),
                r.get("paid_features", ""),
                r.get("language", "English"),
                r.get("official_source", r.get("official_url")),
                r.get("verification_status", "VERIFIED"),
                r.get("last_verified", "2026-09-25"),
                r.get("created_at", "2026-09-25T12:00:00+05:30"),
                r.get("updated_at", "2026-09-25T12:00:00+05:30")
            ))
        conn.commit()
        conn.close()
        print(f"Updated SQLite database at {db_path}")

if __name__ == "__main__":
    main()
