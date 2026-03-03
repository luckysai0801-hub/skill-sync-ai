"""
utils/seed_data.py - Generates 10 sample resumes and 10 sample jobs for demo.

Call this function from main.py startup or run directly:
  python -c "from backend.utils.seed_data import seed_demo_data; seed_demo_data()"
"""

import sys
import os
# Add the backend directory to sys.path so imports match main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal, engine, Base
from models.user import User, UserRole
from models.resume import Resume
from models.job import Job
from services.embedding_service import generate_embedding
from services.resume_scorer import score_resume

# ─── Sample resumes (10 candidates) ───────────────────────────────────────────
SAMPLE_RESUMES = [
    {
        "name": "Candidate A",
        "email": "candidate.a@demo.com",
        "raw_text": """
        Senior Software Engineer with 7 years of experience in Python and JavaScript.
        Built and deployed 3 production microservices on AWS, reducing latency by 40%.
        Led a team of 5 engineers. Improved CI/CD pipeline with GitHub Actions, cutting deploy time by 60%.
        Skills: Python, FastAPI, React, PostgreSQL, Docker, AWS, Redis, REST API, Git.
        Education: Bachelor of Computer Science. Location: San Francisco, California.
        Expected Salary: 130000.
        """,
        "skills": ["python", "fastapi", "react", "postgresql", "docker", "aws", "redis", "rest api", "git"],
        "years_experience": 7.0,
        "education": "Bachelor Of Computer Science",
        "location_city": "San Francisco",
        "location_state": "California",
        "expected_salary": 130000,
    },
    {
        "name": "Candidate B",
        "email": "candidate.b@demo.com",
        "raw_text": """
        Full Stack Developer with 4 years experience. Developed 5 React applications serving 50k+ users.
        Increased application performance by 35% using Redis caching.
        Skills: JavaScript, TypeScript, React, Node.js, MongoDB, Docker, Git, REST API.
        Education: Master of Computer Science. Location: New York, New York.
        Expected Salary: 110000.
        """,
        "skills": ["javascript", "typescript", "react", "node.js", "mongodb", "docker", "git", "rest api"],
        "years_experience": 4.0,
        "education": "Master Of Computer Science",
        "location_city": "New York",
        "location_state": "New York",
        "expected_salary": 110000,
    },
    {
        "name": "Candidate C",
        "email": "candidate.c@demo.com",
        "raw_text": """
        Data Scientist with 5 years in ML/AI. Built predictive models achieving 92% accuracy.
        Reduced customer churn by 25% using scikit-learn models. Published 2 research papers.
        Skills: Python, Machine Learning, Deep Learning, TensorFlow, Scikit-learn, Pandas, NumPy, SQL.
        Education: PhD Data Science. Location: Seattle, Washington.
        Expected Salary: 140000.
        """,
        "skills": ["python", "machine learning", "deep learning", "tensorflow", "scikit-learn", "pandas", "numpy", "sql"],
        "years_experience": 5.0,
        "education": "Phd",
        "location_city": "Seattle",
        "location_state": "Washington",
        "expected_salary": 140000,
    },
    {
        "name": "Candidate D",
        "email": "candidate.d@demo.com",
        "raw_text": """
        DevOps Engineer with 6 years experience. Managed Kubernetes clusters of 200+ nodes.
        Automated infrastructure provisioning with Terraform, saving 30 hours/week.
        Skills: Kubernetes, Docker, AWS, Terraform, Jenkins, Linux, Python, Bash.
        Education: Bachelor Computer Engineering. Location: Austin, Texas.
        Expected Salary: 125000.
        """,
        "skills": ["kubernetes", "docker", "aws", "terraform", "jenkins", "linux", "python", "bash"],
        "years_experience": 6.0,
        "education": "Bachelor",
        "location_city": "Austin",
        "location_state": "Texas",
        "expected_salary": 125000,
    },
    {
        "name": "Candidate E",
        "email": "candidate.e@demo.com",
        "raw_text": """
        Junior Software Developer, 2 years experience. Built 3 REST APIs using Django.
        Implemented authentication systems for 10k+ users. Contributed to open source projects.
        Skills: Python, Django, JavaScript, React, MySQL, Git.
        Education: Bachelor Computer Science. Location: Chicago, Illinois.
        Expected Salary: 75000.
        """,
        "skills": ["python", "django", "javascript", "react", "mysql", "git"],
        "years_experience": 2.0,
        "education": "Bachelor",
        "location_city": "Chicago",
        "location_state": "Illinois",
        "expected_salary": 75000,
    },
    {
        "name": "Candidate F",
        "email": "candidate.f@demo.com",
        "raw_text": """
        AI/ML Engineer with 3 years experience. Fine-tuned LLM models (GPT, BERT) for NLP tasks.
        Achieved 15% improvement in BLEU score. Deployed models on GCP with 99.9% uptime.
        Skills: Python, PyTorch, LLM, Generative AI, Hugging Face, LangChain, GCP, Docker.
        Education: Master Artificial Intelligence. Location: Remote.
        Expected Salary: 135000.
        """,
        "skills": ["python", "pytorch", "llm", "generative ai", "hugging face", "langchain", "gcp", "docker"],
        "years_experience": 3.0,
        "education": "Master",
        "location_city": "Remote",
        "location_state": "Remote",
        "expected_salary": 135000,
    },
    {
        "name": "Candidate G",
        "email": "candidate.g@demo.com",
        "raw_text": """
        Backend Engineer 8 years. Designed microservices architecture serving 5M requests/day.
        Optimized PostgreSQL queries, reducing p99 latency from 500ms to 80ms.
        Skills: Java, Spring Boot, Microservices, PostgreSQL, Kafka, Redis, Docker, Kubernetes.
        Education: Bachelor Computer Science. Location: Boston, Massachusetts.
        Expected Salary: 145000.
        """,
        "skills": ["java", "spring boot", "microservices", "postgresql", "kafka", "redis", "docker", "kubernetes"],
        "years_experience": 8.0,
        "education": "Bachelor",
        "location_city": "Boston",
        "location_state": "Massachusetts",
        "expected_salary": 145000,
    },
    {
        "name": "Candidate H",
        "email": "candidate.h@demo.com",
        "raw_text": """
        Data Engineer 4 years. Built ETL pipelines processing 100GB+ daily with Apache Spark.
        Reduced data processing time by 50%. Created dashboards for 200+ business stakeholders.
        Skills: Python, Apache Spark, Kafka, Airflow, SQL, AWS, Snowflake, dbt.
        Education: Bachelor Data Engineering. Location: Denver, Colorado.
        Expected Salary: 115000.
        """,
        "skills": ["python", "spark", "kafka", "airflow", "sql", "aws", "snowflake", "dbt"],
        "years_experience": 4.0,
        "education": "Bachelor",
        "location_city": "Denver",
        "location_state": "Colorado",
        "expected_salary": 115000,
    },
    {
        "name": "Candidate I",
        "email": "candidate.i@demo.com",
        "raw_text": """
        Frontend Developer 3 years. Built component libraries used by 20+ teams.
        Increased web application load speed by 45% through optimization.
        Skills: JavaScript, TypeScript, React, Next.js, TailwindCSS, GraphQL, Git.
        Education: Bachelor Software Engineering. Location: Los Angeles, California.
        Expected Salary: 95000.
        """,
        "skills": ["javascript", "typescript", "react", "next.js", "graphql", "git"],
        "years_experience": 3.0,
        "education": "Bachelor",
        "location_city": "Los Angeles",
        "location_state": "California",
        "expected_salary": 95000,
    },
    {
        "name": "Candidate J",
        "email": "candidate.j@demo.com",
        "raw_text": """
        Security Engineer 5 years. Conducted 30+ penetration tests; reduced vulnerabilities by 70%.
        Automated security scanning in CI/CD pipelines. Achieved SOC2 compliance for 3 organizations.
        Skills: Python, Kubernetes, AWS, Linux, Docker, Security, Bash, Git.
        Education: Master Cybersecurity. Location: Washington, DC.
        Expected Salary: 130000.
        """,
        "skills": ["python", "kubernetes", "aws", "linux", "docker", "bash", "git"],
        "years_experience": 5.0,
        "education": "Master",
        "location_city": "Washington",
        "location_state": "DC",
        "expected_salary": 130000,
    },
]

# ─── Sample jobs (10 job postings) ────────────────────────────────────────────
SAMPLE_JOBS = [
    {
        "title": "Senior Python Backend Engineer",
        "description": "Build scalable FastAPI microservices. You will design RESTful APIs, manage PostgreSQL databases, and deploy on AWS using Docker and Kubernetes.",
        "required_skills": ["python", "fastapi", "postgresql", "docker", "aws", "rest api"],
        "required_experience": 5.0, "salary_min": 120000, "salary_max": 160000,
        "location_city": "San Francisco", "location_state": "California", "is_remote": False,
    },
    {
        "title": "Full Stack React Developer",
        "description": "Develop responsive React applications with Node.js backends. Collaborate with UX team to build beautiful user interfaces and integrate REST APIs.",
        "required_skills": ["javascript", "typescript", "react", "node.js", "rest api", "git"],
        "required_experience": 3.0, "salary_min": 90000, "salary_max": 130000,
        "location_city": "New York", "location_state": "New York", "is_remote": False,
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Design and deploy ML models for recommendation systems and predictive analytics. Work with large-scale datasets and production ML pipelines.",
        "required_skills": ["python", "machine learning", "scikit-learn", "tensorflow", "sql", "docker"],
        "required_experience": 4.0, "salary_min": 130000, "salary_max": 170000,
        "location_city": "Seattle", "location_state": "Washington", "is_remote": True,
    },
    {
        "title": "DevOps / Cloud Engineer",
        "description": "Manage cloud infrastructure on AWS. Automate deployments with Kubernetes and Terraform. Maintain CI/CD pipelines and ensure 99.9% uptime.",
        "required_skills": ["kubernetes", "docker", "aws", "terraform", "linux", "python"],
        "required_experience": 4.0, "salary_min": 115000, "salary_max": 150000,
        "location_city": "Austin", "location_state": "Texas", "is_remote": False,
    },
    {
        "title": "AI / LLM Engineer",
        "description": "Fine-tune and deploy large language models. Build RAG pipelines using LangChain and vector databases. Deploy AI services on GCP.",
        "required_skills": ["python", "pytorch", "llm", "generative ai", "langchain", "gcp"],
        "required_experience": 2.0, "salary_min": 125000, "salary_max": 165000,
        "location_city": "Remote", "location_state": "Remote", "is_remote": True,
    },
    {
        "title": "Java Microservices Architect",
        "description": "Design distributed systems using Java and Spring Boot. Lead architecture decisions for high-throughput services processing millions of requests.",
        "required_skills": ["java", "spring boot", "microservices", "kafka", "postgresql", "kubernetes"],
        "required_experience": 6.0, "salary_min": 140000, "salary_max": 180000,
        "location_city": "Boston", "location_state": "Massachusetts", "is_remote": False,
    },
    {
        "title": "Data Engineer",
        "description": "Build and maintain scalable data pipelines. Work with Spark, Kafka, and Airflow to process large datasets and feed analytics dashboards.",
        "required_skills": ["python", "spark", "kafka", "airflow", "sql", "aws"],
        "required_experience": 3.0, "salary_min": 110000, "salary_max": 140000,
        "location_city": "Denver", "location_state": "Colorado", "is_remote": False,
    },
    {
        "title": "Frontend Engineer (React/TypeScript)",
        "description": "Build next-generation frontend applications with React and TypeScript. Optimize performance and accessibility for millions of users.",
        "required_skills": ["javascript", "typescript", "react", "next.js", "git"],
        "required_experience": 2.0, "salary_min": 85000, "salary_max": 120000,
        "location_city": "Los Angeles", "location_state": "California", "is_remote": True,
    },
    {
        "title": "Junior Python Developer",
        "description": "Join our growing team to build backend services with Python and Django. Great opportunity to learn modern development practices.",
        "required_skills": ["python", "django", "sql", "git", "rest api"],
        "required_experience": 1.0, "salary_min": 65000, "salary_max": 90000,
        "location_city": "Chicago", "location_state": "Illinois", "is_remote": False,
    },
    {
        "title": "Cloud Security Engineer",
        "description": "Secure cloud infrastructure on AWS. Conduct security reviews, automate compliance checks, and manage IAM policies. Kubernetes expertise required.",
        "required_skills": ["python", "kubernetes", "aws", "linux", "docker", "bash"],
        "required_experience": 4.0, "salary_min": 120000, "salary_max": 155000,
        "location_city": "Washington", "location_state": "DC", "is_remote": False,
    },
]

# ─── Employer users (2 employers for 10 jobs) ---------------------------------
EMPLOYER_USERS = [
    {"email": "employer1@techcorp.com", "name": "TechCorp HR"},
    {"email": "employer2@innovate.io", "name": "Innovate.io Recruiting"},
]


def seed_demo_data():
    """Create all demo users, resumes, and jobs in the database."""
    # Ensure tables exist
    import models.user   # noqa – imports trigger table creation
    import models.resume  # noqa
    import models.job     # noqa
    import models.match   # noqa
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("✅ Demo data already exists – skipping seed.")
            return

        print("🌱 Seeding demo data...")

        # ── Create employer users ──────────────────────────────────────────────
        employers = []
        for emp in EMPLOYER_USERS:
            user = User(email=emp["email"], name=emp["name"], role=UserRole.employer)
            db.add(user)
            db.flush()
            employers.append(user)

        # ── Create candidate users + resumes ───────────────────────────────────
        for i, rd in enumerate(SAMPLE_RESUMES):
            user = User(email=rd["email"], name=rd["name"], role=UserRole.candidate)
            db.add(user)
            db.flush()

            text = rd["raw_text"].strip()
            emb = generate_embedding(text)
            score_result = score_resume(text, rd["skills"])

            resume = Resume(
                user_id=user.id,
                raw_text=text,
                skills=rd["skills"],
                years_experience=rd["years_experience"],
                education=rd["education"],
                location_city=rd["location_city"],
                location_state=rd["location_state"],
                expected_salary=rd["expected_salary"],
                embedding=emb,
                resume_score=score_result["resume_score"],
                improvement_suggestions=score_result["improvement_suggestions"],
            )
            db.add(resume)
            print(f"  ✔ Resume {i+1}/10 created")

        # ── Create jobs ────────────────────────────────────────────────────────
        for i, jd in enumerate(SAMPLE_JOBS):
            emp = employers[i % len(employers)]
            combined = f"{jd['title']}. {jd['description']}. Skills: {', '.join(jd['required_skills'])}"
            emb = generate_embedding(combined)

            job = Job(
                employer_id=emp.id,
                title=jd["title"],
                description=jd["description"],
                required_skills=jd["required_skills"],
                required_experience=jd["required_experience"],
                salary_min=jd["salary_min"],
                salary_max=jd["salary_max"],
                location_city=jd["location_city"],
                location_state=jd["location_state"],
                is_remote=jd["is_remote"],
                embedding=emb,
            )
            db.add(job)
            print(f"  ✔ Job {i+1}/10 created")

        db.commit()
        print("✅ Demo data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
