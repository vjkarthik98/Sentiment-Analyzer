# 🤖 Gen AI Sentiment Analysis Project (CI/CD Pipeline)

This is a full-stack, AI-powered web application that uses a Hugging Face model for real-time sentiment analysis.

This project has been re-architected from a simple deployment to a professional, automated **CI/CD pipeline**. When new code is pushed to the `main` branch, a GitHub Actions workflow automatically builds a Docker container, pushes it to a private registry (AWS ECR), and deploys the new version to a live server (AWS EC2) with zero downtime.

This project uses a modern, **keyless** authentication method (IAM OIDC) for secure communication between GitHub and AWS, which is a production best practice.

**Live Demo:** `http://[Your-EC2-Public-IP]:5000/app`

---

## 🚀 CI/CD Architecture

This is not just a project, but a demonstration of a complete, automated deployment system.

1.  **Code:** A developer pushes a `git commit` to the `main` branch on GitHub.
2.  **CI (Continuous Integration):** This push triggers a **GitHub Actions** workflow.
3.  **Build:** The workflow builds the Flask application into a **Docker** container.
4.  **Store:** The Docker image is tagged and pushed to a private **Amazon ECR** (Elastic Container Registry).
5.  **CD (Continuous Deployment):** The GitHub Action securely connects to AWS using an **IAM OIDC** role (no secret keys!).
6.  **Deploy:** The Action sends a command to the **Amazon EC2** server using **AWS SSM** (Systems Manager). The server pulls the new image from ECR, stops the old container, and runs the new one.



---

## 🛠️ Tech Stack

* **AI/ML:** Hugging Face `transformers` (`distilbert-base-uncased-finetuned-sst-2-english`)
* **Backend:** Flask (Python)
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Containerization:** Docker
* **Cloud & Deployment:**
    * **CI/CD:** GitHub Actions
    * **Compute:** Amazon EC2 (t2.micro)
    * **Container Registry:** Amazon ECR (Elastic Container Registry)
    * **Secure Comms:** AWS IAM (OIDC Identity Provider) & AWS SSM (Systems Manager)

---

## 📜 Responsible AI & Ethics

This is a **critical** part of any AI project.

* **Model:** This project uses `distilbert-base-uncased-finetuned-sst-2-english`.
* **Training Data:** This model was fine-tuned on the **SST-2 dataset**, which consists of **movie reviews**.
* **Known Limitations & Bias:**
    * **Domain Mismatch:** Because it was trained on movie reviews, it performs best on similar language. It may be less accurate for technical, financial, or medical text.
    * **Sarcasm & Irony:** The model cannot reliably detect sarcasm. A statement like "This app is *so* fast" (when it's slow) will likely be misclassified as `POSITIVE`.
    * **Complex Negation:** It can struggle with complex sentences like "I don't dislike this, but I wouldn't recommend it either."

* **Ethical Use:** This tool is for demonstration and educational purposes only. It should **not** be used as the sole factor in making decisions about individuals (e.g., scoring customer support chats for employee reviews, filtering job applications).

---

## 🔧 How It Works (Setup & Configuration)

This setup is fully reproducible for a portfolio.

### 1. AWS Infrastructure Setup

1.  **ECR:** A private ECR repository named `sentiment-analyzer` was created to store the Docker images.
2.  **IAM (for EC2):** An IAM Role (`ec2-ssm-ecr-role`) was created for the EC2 instance. It has two policies:
    * `AmazonSSMManagedInstanceCore`: Allows AWS Systems Manager to send commands (like "deploy").
    * `AmazonEC2ContainerRegistryReadOnly`: Allows the server to pull images from ECR.
3.  **IAM (for GitHub Actions):** An OIDC Identity Provider was configured in IAM, establishing trust with GitHub. A role (`github-actions-role`) was created for this provider, granting permission to:
    * `AmazonEC2ContainerRegistryPowerUser`: Allows GitHub to push images *to* ECR.
    * `AmazonSSMFullAccess`: Allows GitHub to send deployment commands *to* the EC2 instance.
4.  **EC2:** A `t2.micro` instance was launched with the `Amazon Linux 2` AMI.
    * **Security Group:** Port `5000` was opened to `0.0.0.0/0` to allow public traffic to the Flask app.
    * **IAM Role:** The `ec2-ssm-ecr-role` was attached.
    * **User Data:** This script was used on launch to install and start Docker.
        ```bash
        #!/bin/bash
        yum update -y
        yum install docker -y
        service docker start
        usermod -a -G docker ec2-user
        ```

### 2. Project Files

* **`Dockerfile`**: Defines the recipe to build the app, install `requirements.txt`, and run it with a `gunicorn` production server.
* **`application.py`**: The Flask backend API, complete with error handling and model loading.
* **`.github/workflows/main.yml`**: The "brain" of the CI/CD pipeline.
    1.  **Triggers** on a push to `main`.
    2.  **Configures** AWS credentials securely using the OIDC role.
    3.  **Logs in** to Amazon ECR.
    4.  **Builds & Pushes** the Docker image.
    5.  **Deploys** by sending a `docker pull` and `docker run` command to the EC2 instance via AWS SSM.