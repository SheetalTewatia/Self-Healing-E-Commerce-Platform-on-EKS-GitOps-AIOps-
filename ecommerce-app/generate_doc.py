"""
Generate a detailed Word document for the ShopEasy DevOps project.
Run: python generate_doc.py
Output: ShopEasy_DevOps_Project.docx
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ── Page margins ────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Helpers ──────────────────────────────────────────────────────────────────

def heading(text, level=1, color=None):
    p = doc.add_heading(text, level=level)
    if color:
        for run in p.runs:
            run.font.color.rgb = RGBColor(*color)
    return p

def para(text, bold=False, size=11, color=None, align=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return p

def code_block(text):
    p = doc.add_paragraph()
    p.style = doc.styles['No Spacing']
    run = p.add_run(text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0xD4, 0x00, 0x00)
    shading = OxmlElement('w:shd')
    shading.set(qn('w:val'), 'clear')
    shading.set(qn('w:color'), 'auto')
    shading.set(qn('w:fill'), 'F5F5F5')
    p._p.get_or_add_pPr().append(shading)
    return p

def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        run = cell.paragraphs[0].runs[0]
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shading = OxmlElement('w:shd')
        shading.set(qn('w:val'), 'clear')
        shading.set(qn('w:color'), 'auto')
        shading.set(qn('w:fill'), '1F4E79')
        cell._tc.get_or_add_tcPr().append(shading)
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        fill = 'DEEAF1' if r_idx % 2 == 0 else 'FFFFFF'
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(10)
            shading = OxmlElement('w:shd')
            shading.set(qn('w:val'), 'clear')
            shading.set(qn('w:color'), 'auto')
            shading.set(qn('w:fill'), fill)
            cell._tc.get_or_add_tcPr().append(shading)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    return table

def add_image(path, caption, width=Inches(5.5)):
    if os.path.exists(path):
        doc.add_picture(path, width=width)
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = doc.add_paragraph(caption)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.size = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    else:
        p = doc.add_paragraph(f'[Screenshot: {caption}]')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.size = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

def divider():
    doc.add_paragraph('─' * 80)

# ════════════════════════════════════════════════════════════════════════════
#  COVER PAGE
# ════════════════════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run('End-to-End DevOps Pipeline on AWS')
r.font.size = Pt(28)
r.bold = True
r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub.add_run('ShopEasy E-Commerce Platform')
r2.font.size = Pt(20)
r2.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

doc.add_paragraph()
line = doc.add_paragraph()
line.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = line.add_run('─' * 50)
r3.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

doc.add_paragraph()
stack = doc.add_paragraph()
stack.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = stack.add_run('GitHub  →  Jenkins  →  Maven  →  SonarQube  →  Trivy\n'
                   'Docker  →  AWS ECR  →  ArgoCD  →  AWS EKS\n'
                   'Prometheus  +  Grafana  |  Terraform IaC')
r4.font.size = Pt(13)
r4.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

doc.add_paragraph()
doc.add_paragraph()

author = doc.add_paragraph()
author.alignment = WD_ALIGN_PARAGRAPH.CENTER
ra = author.add_run('Chirag Goyal\nDevOps Engineering Project\nApril 2026')
ra.font.size = Pt(12)
ra.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  1. PROJECT OVERVIEW
# ════════════════════════════════════════════════════════════════════════════

heading('1. Project Overview', 1, (0x1F, 0x4E, 0x79))

para(
    'This project demonstrates a production-grade, end-to-end DevOps pipeline on AWS. '
    'The goal was to build a real microservices application and automate the complete lifecycle — '
    'from a developer pushing code to it being live in production — using industry-standard DevOps tools.',
    size=11
)
doc.add_paragraph()
para('What makes this project complete:', bold=True)
doc.add_paragraph()

points = [
    ('Infrastructure as Code', 'All AWS resources (VPC, EC2, EKS, ECR, IAM) provisioned with Terraform — zero manual clicking in the AWS console'),
    ('Continuous Integration', 'Jenkins automates build, test, static analysis, security scan, and image push on every git push'),
    ('GitOps Continuous Delivery', 'ArgoCD watches a git repository and auto-deploys to Kubernetes — git is the single source of truth'),
    ('Real Application', 'A working e-commerce platform (ShopEasy) with 4 Spring Boot microservices, API Gateway, React frontend, and MongoDB'),
    ('Production Monitoring', 'Prometheus + Grafana installed on the cluster providing real-time dashboards for every pod and node'),
]

for title_text, desc in points:
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(f'{title_text}: ')
    r.bold = True
    r.font.size = Pt(11)
    p.add_run(desc).font.size = Pt(11)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  2. ARCHITECTURE
# ════════════════════════════════════════════════════════════════════════════

heading('2. Architecture Overview', 1, (0x1F, 0x4E, 0x79))

para('The pipeline follows a two-phase architecture:', bold=True)
doc.add_paragraph()

heading('CI Phase (Jenkins on EC2)', 2, (0x2E, 0x75, 0xB6))
code_block(
    'Developer pushes code\n'
    '    │\n'
    '    ▼ GitHub Webhook\n'
    'Jenkins EC2 (t3.medium)\n'
    '    ├─► Maven Build & Test    (parallel: 4 services)\n'
    '    ├─► SonarQube Analysis    (parallel: 4 services)\n'
    '    ├─► Quality Gate          (blocks if code quality fails)\n'
    '    ├─► Docker Build          (parallel: 6 images)\n'
    '    ├─► Trivy Security Scan   (sequential: 6 images)\n'
    '    ├─► Push to AWS ECR       (6 repositories)\n'
    '    └─► Update ecommerce-config repo (new image tags)\n'
)

doc.add_paragraph()
heading('CD Phase (ArgoCD on EKS)', 2, (0x2E, 0x75, 0xB6))
code_block(
    'ecommerce-config repo updated\n'
    '    │\n'
    '    ▼ ArgoCD detects git diff\n'
    'ArgoCD (running inside EKS)\n'
    '    ├─► Computes diff: git state vs cluster state\n'
    '    ├─► Applies changed manifests via kubectl\n'
    '    ├─► Kubernetes pulls new images from ECR\n'
    '    ├─► Rolling update (zero downtime)\n'
    '    └─► Readiness probes verify pod health\n'
    '\n'
    'AWS EKS Cluster (2x t3.medium nodes)\n'
    '    ├─ Namespace: ecommerce\n'
    '    │    ├─ user-service          (port 8081)\n'
    '    │    ├─ product-service       (port 8082)\n'
    '    │    ├─ order-service         (port 8083)\n'
    '    │    ├─ notification-service  (port 8084)\n'
    '    │    ├─ api-gateway           (port 8080)\n'
    '    │    ├─ frontend              (port 80)   ← AWS LoadBalancer\n'
    '    │    └─ mongodb-0             (port 27017) ← StatefulSet + EBS PV\n'
    '    ├─ Namespace: argocd\n'
    '    └─ Namespace: monitoring\n'
    '         ├─ prometheus\n'
    '         └─ grafana              ← AWS LoadBalancer\n'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  3. TECH STACK
# ════════════════════════════════════════════════════════════════════════════

heading('3. Technology Stack', 1, (0x1F, 0x4E, 0x79))

add_table(
    ['Category', 'Tool / Service', 'Version', 'Purpose'],
    [
        ['Source Control',         'GitHub',                    '—',           'Stores app code + K8s manifests (2 repos)'],
        ['IaC',                    'Terraform',                 '≥ 1.5',       'Provisions all AWS resources as code'],
        ['CI Server',              'Jenkins',                   'LTS',         'Orchestrates build → test → scan → push pipeline'],
        ['Build Tool',             'Apache Maven',              '3.9',         'Compiles Java services, runs unit tests'],
        ['Code Quality',           'SonarQube',                 'LTS Community','Static analysis, code smell, vulnerability detection'],
        ['Security Scan',          'Trivy',                     'Latest',      'Scans Docker images for CVEs (OS + JAR dependencies)'],
        ['Container Registry',     'AWS ECR',                   '—',           'Private Docker image registry (6 repos)'],
        ['Container Runtime',      'Docker',                    '24+',         'Builds and runs containers'],
        ['Orchestration',          'AWS EKS',                   '1.32',        'Managed Kubernetes — runs microservices in prod'],
        ['GitOps CD',              'ArgoCD',                    'Stable',      'Watches config repo, auto-deploys to K8s'],
        ['Monitoring',             'Prometheus + Grafana',      'Helm chart',  'Metrics collection and visualization dashboards'],
        ['Backend Framework',      'Spring Boot',               '3.2',         'Java microservices framework'],
        ['API Gateway',            'Spring Cloud Gateway',      '4.x',         'Routes and filters all API requests (WebFlux)'],
        ['Database',               'MongoDB',                   '7.0',         'NoSQL document store for all 4 services'],
        ['Frontend',               'Nginx + HTML/CSS/JS',       '—',           'Serves the ShopEasy web UI'],
        ['Persistent Storage',     'AWS EBS (gp2)',              '—',           'Persistent volume for MongoDB StatefulSet'],
        ['Load Balancer',          'AWS ELB (Classic)',         '—',           'Exposes frontend and Grafana to the internet'],
    ],
    [1.3, 1.6, 1.0, 2.6]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  4. PHASE 1 — TERRAFORM INFRASTRUCTURE
# ════════════════════════════════════════════════════════════════════════════

heading('4. Phase 1 — Infrastructure Provisioning (Terraform)', 1, (0x1F, 0x4E, 0x79))

para(
    'All AWS infrastructure is defined as code in the terraform/ directory. '
    'Running terraform apply creates the complete environment in ~15 minutes.',
    size=11
)

heading('4.1 Networking (VPC)', 2, (0x2E, 0x75, 0xB6))
add_table(
    ['Resource', 'Configuration', 'Why'],
    [
        ['VPC',              '10.0.0.0/16 CIDR',                            'Isolated network for all resources'],
        ['Public Subnets',   '2x subnets in us-east-1a and us-east-1b',     'Jenkins, SonarQube, NAT Gateway, Load Balancers'],
        ['Private Subnets',  '2x subnets in us-east-1a and us-east-1b',     'EKS worker nodes — not directly internet-accessible'],
        ['Internet Gateway', 'Attached to VPC',                             'Allows public subnets to reach the internet'],
        ['NAT Gateway',      '1x in public subnet + Elastic IP',            'Allows private EKS nodes to pull images from ECR'],
        ['Route Tables',     'Public → IGW, Private → NAT',                 'Controls traffic flow for each subnet tier'],
    ],
    [1.5, 2.5, 2.5]
)

doc.add_paragraph()
heading('4.2 Compute', 2, (0x2E, 0x75, 0xB6))
add_table(
    ['Resource', 'Spec', 'Purpose'],
    [
        ['Jenkins EC2',       't3.medium, 30 GB, Amazon Linux 2023, public subnet',  'CI server — runs Jenkins pipeline'],
        ['SonarQube EC2',     't3.medium, 30 GB, Amazon Linux 2023, public subnet',  'Code quality analysis server'],
        ['EKS Node Group',    '2x t3.medium, private subnets, auto-scaling 1–3',     'Runs all Kubernetes workloads'],
        ['EKS Control Plane', 'AWS-managed, EKS v1.32',                              'Kubernetes API server, etcd, scheduler'],
    ],
    [1.5, 3.0, 2.0]
)

doc.add_paragraph()
heading('4.3 ECR Repositories', 2, (0x2E, 0x75, 0xB6))
para('Six private ECR repositories created via Terraform for_each loop:', size=11)
code_block(
    'locals {\n'
    '  services = ["user-service","product-service","order-service",\n'
    '              "notification-service","api-gateway","frontend"]\n'
    '}\n'
    'resource "aws_ecr_repository" "services" {\n'
    '  for_each             = toset(local.services)\n'
    '  name                 = each.key\n'
    '  image_tag_mutability = "MUTABLE"\n'
    '  image_scanning_configuration { scan_on_push = true }\n'
    '}'
)

doc.add_paragraph()
heading('4.4 IAM Roles', 2, (0x2E, 0x75, 0xB6))
add_table(
    ['IAM Role', 'Policies Attached', 'Used By'],
    [
        ['devops-demo-eks-cluster-role', 'AmazonEKSClusterPolicy',                                              'EKS control plane'],
        ['devops-demo-eks-node-role',    'AmazonEKSWorkerNodePolicy, AmazonEKS_CNI_Policy, EC2ContainerRegistryReadOnly', 'EKS worker nodes'],
        ['jenkins-ec2-role',            'AmazonEC2ContainerRegistryFullAccess, AmazonEBSCSIDriverPolicy',       'Jenkins EC2 (no stored credentials)'],
    ],
    [2.0, 3.0, 1.5]
)

doc.add_paragraph()
heading('4.5 Terraform Commands', 2, (0x2E, 0x75, 0xB6))
code_block(
    '# Step 1 — Create EC2 key pair\n'
    'aws ec2 create-key-pair --key-name devops-key \\\n'
    '  --query "KeyMaterial" --output text > devops-key.pem\n'
    'chmod 400 devops-key.pem\n\n'
    '# Step 2 — Initialize and apply\n'
    'cd terraform/\n'
    'terraform init\n'
    'terraform plan    # Review what will be created\n'
    'terraform apply   # Type "yes" to confirm\n\n'
    '# ~15 minutes later, outputs:\n'
    '# eks_cluster_name    = "devops-demo-cluster"\n'
    '# jenkins_public_ip   = "34.205.90.146"\n'
    '# sonarqube_public_ip = "3.87.42.29"\n'
    '# ecr_base_url        = "535355705679.dkr.ecr.us-east-1.amazonaws.com"'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  5. PHASE 2 — JENKINS SETUP
# ════════════════════════════════════════════════════════════════════════════

heading('5. Phase 2 — Jenkins CI Server Setup', 1, (0x1F, 0x4E, 0x79))

para(
    'Jenkins runs on the EC2 instance provisioned by Terraform. '
    'The following software must be installed on the Jenkins EC2.',
    size=11
)

heading('5.1 Software Installation on Jenkins EC2', 2, (0x2E, 0x75, 0xB6))
code_block(
    '# SSH into Jenkins EC2\n'
    'ssh -i devops-key.pem ec2-user@<JENKINS_IP>\n\n'
    '# Java 21 (Jenkins requires Java 17+)\n'
    'sudo dnf install java-21-amazon-corretto -y\n'
    'echo "JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto" | sudo tee -a /etc/sysconfig/jenkins\n\n'
    '# Jenkins\n'
    'sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo\n'
    'sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key\n'
    'sudo dnf install jenkins -y\n'
    'sudo systemctl enable --now jenkins\n\n'
    '# Docker\n'
    'sudo dnf install docker -y\n'
    'sudo systemctl enable --now docker\n'
    'sudo usermod -aG docker jenkins\n'
    'sudo chmod 666 /var/run/docker.sock\n\n'
    '# Maven 3.9\n'
    'cd /opt && sudo wget https://downloads.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz\n'
    'sudo tar -xzf apache-maven-3.9.6-bin.tar.gz\n'
    'sudo ln -s /opt/apache-maven-3.9.6 /opt/maven\n'
    'echo "export PATH=/opt/maven/bin:$PATH" | sudo tee /etc/profile.d/maven.sh\n\n'
    '# AWS CLI v2\n'
    'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip\n'
    'unzip awscliv2.zip && sudo ./aws/install\n\n'
    '# kubectl\n'
    'cd ~ && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"\n'
    'sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl\n\n'
    '# Trivy\n'
    'sudo rpm -ivh https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.rpm'
)

heading('5.2 Jenkins Plugin Configuration', 2, (0x2E, 0x75, 0xB6))
para('Install these plugins via Manage Jenkins → Plugins → Available:', size=11)
add_table(
    ['Plugin', 'Purpose'],
    [
        ['Docker Pipeline',        'Allows building Docker images inside Jenkinsfile'],
        ['SonarQube Scanner',      'Integrates SonarQube analysis into Jenkins pipeline'],
        ['GitHub Integration',     'Receives GitHub webhooks to trigger builds'],
        ['Pipeline',               'Enables declarative Jenkinsfile pipelines'],
        ['Credentials Binding',    'Injects secrets into pipeline environment variables'],
        ['Git',                    'Clones GitHub repositories in pipeline'],
    ],
    [2.0, 4.5]
)

doc.add_paragraph()
heading('5.3 Jenkins System Configuration', 2, (0x2E, 0x75, 0xB6))
para('Configure at Manage Jenkins → System:', size=11)
points2 = [
    'SonarQube Server: Name = SonarQube, URL = http://<SONAR_IP>:9000, token from credentials',
    'Global Tool Configuration → Maven → Name = Maven, MAVEN_HOME = /opt/maven',
    'Credentials → Add → GitHub username+token (ID: github-creds)',
    'Credentials → Add → SonarQube secret text token',
]
for pt in points2:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(pt).font.size = Pt(11)

doc.add_paragraph()
heading('5.4 SonarQube Webhook (Critical)', 2, (0x2E, 0x75, 0xB6))
para(
    'SonarQube must send the Quality Gate result back to Jenkins. '
    'Without this, the pipeline hangs waiting for a result that never arrives.',
    size=11
)
code_block(
    'SonarQube UI → Administration → Webhooks → Create\n'
    '  Name: Jenkins\n'
    '  URL:  http://<JENKINS_IP>:8080/sonarqube-webhook/\n'
    '  (no trailing slash on the webhook path)'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  6. PHASE 3 — SONARQUBE SETUP
# ════════════════════════════════════════════════════════════════════════════

heading('6. Phase 3 — SonarQube Setup', 1, (0x1F, 0x4E, 0x79))

para('SonarQube runs as a Docker container on its dedicated EC2 instance.', size=11)

code_block(
    '# SSH into SonarQube EC2\n'
    'ssh -i devops-key.pem ec2-user@<SONARQUBE_IP>\n\n'
    '# Install and start Docker\n'
    'sudo dnf install docker -y\n'
    'sudo systemctl enable --now docker\n\n'
    '# Run SonarQube (LTS Community Edition)\n'
    'docker run -d \\\n'
    '  --name sonarqube \\\n'
    '  --restart unless-stopped \\\n'
    '  -p 9000:9000 \\\n'
    '  sonarqube:lts-community\n\n'
    '# Access at: http://<SONARQUBE_IP>:9000\n'
    '# Default login: admin / admin → change on first login'
)

doc.add_paragraph()
para('SonarQube analyses 4 quality dimensions for each Java service:', size=11)
add_table(
    ['Dimension', 'What It Checks', 'Failure Threshold (default)'],
    [
        ['Reliability',  'Bugs in code logic',                           '> 0 blocker bugs'],
        ['Security',     'Vulnerabilities (SQL injection, XSS, etc.)',   '> 0 critical vulnerabilities'],
        ['Maintainability', 'Code smells, technical debt',              '> A rating'],
        ['Coverage',     'Unit test code coverage',                      '< 80% (configurable)'],
    ],
    [1.5, 3.0, 2.0]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  7. PHASE 4 — CI PIPELINE (JENKINSFILE)
# ════════════════════════════════════════════════════════════════════════════

heading('7. Phase 4 — CI Pipeline Deep Dive (Jenkinsfile)', 1, (0x1F, 0x4E, 0x79))

para(
    'The Jenkinsfile at the root of ecommerce-app defines a 7-stage declarative pipeline. '
    'Every git push to main triggers the full pipeline via GitHub webhook.',
    size=11
)

heading('Stage 1: Maven Build & Test (Parallel)', 2, (0x2E, 0x75, 0xB6))
para('All 4 Java services compile and run tests simultaneously:', size=11)
code_block(
    'stage("Maven Build & Test") {\n'
    '    parallel {\n'
    '        stage("user-service")         { steps { dir("user-service")         { sh "mvn clean package -B" } } }\n'
    '        stage("product-service")      { steps { dir("product-service")      { sh "mvn clean package -B" } } }\n'
    '        stage("order-service")        { steps { dir("order-service")        { sh "mvn clean package -B" } } }\n'
    '        stage("notification-service") { steps { dir("notification-service") { sh "mvn clean package -B" } } }\n'
    '    }\n'
    '}'
)
para('If any service fails to compile or a test fails, the pipeline stops here. No Docker images are built.', size=11)

doc.add_paragraph()
heading('Stage 2: SonarQube Analysis (Parallel)', 2, (0x2E, 0x75, 0xB6))
code_block(
    'stage("SonarQube Analysis") {\n'
    '    steps {\n'
    '        withSonarQubeEnv("SonarQube") {\n'
    '            script {\n'
    '                parallel(\n'
    '                    "user-service":    { dir("user-service")    { sh "mvn sonar:sonar -Dsonar.projectKey=user-service -B" } },\n'
    '                    "product-service": { dir("product-service") { sh "mvn sonar:sonar -Dsonar.projectKey=product-service -B" } },\n'
    '                    ...\n'
    '                )\n'
    '            }\n'
    '        }\n'
    '    }\n'
    '}'
)

doc.add_paragraph()
heading('Stage 3: Quality Gate', 2, (0x2E, 0x75, 0xB6))
code_block(
    'stage("Quality Gate") {\n'
    '    steps {\n'
    '        timeout(time: 5, unit: "MINUTES") {\n'
    '            waitForQualityGate abortPipeline: true\n'
    '        }\n'
    '    }\n'
    '}'
)
para(
    'Jenkins pauses here and waits for SonarQube to send a webhook callback with PASS or FAIL. '
    'abortPipeline: true means a FAIL kills the entire pipeline — nothing gets deployed.',
    size=11
)

doc.add_paragraph()
heading('Stage 4: Docker Build (Parallel)', 2, (0x2E, 0x75, 0xB6))
para('All 6 images build simultaneously using multi-stage Dockerfiles:', size=11)
code_block(
    '# Multi-stage Dockerfile pattern (Java services)\n'
    'FROM maven:3.9-eclipse-temurin-21 AS build\n'
    'WORKDIR /app\n'
    'COPY pom.xml .\n'
    'RUN mvn dependency:go-offline -B        # Cache dependencies layer\n'
    'COPY src ./src\n'
    'RUN mvn clean package -DskipTests -B\n\n'
    'FROM eclipse-temurin:21-jre-alpine      # Lean runtime image (~200MB)\n'
    'WORKDIR /app\n'
    'COPY --from=build /app/target/*.jar app.jar\n'
    'EXPOSE 8081\n'
    'ENTRYPOINT ["java","-jar","app.jar"]'
)

doc.add_paragraph()
heading('Stage 5: Trivy Security Scan (Sequential)', 2, (0x2E, 0x75, 0xB6))
para(
    'Trivy scans each Docker image for known CVEs. Running sequentially avoids cache file lock conflicts. '
    '--exit-code 0 reports findings without blocking the pipeline.',
    size=11
)
code_block(
    'stage("Trivy Security Scan") {\n'
    '    environment {\n'
    '        TMPDIR = "/var/lib/jenkins/trivy-tmp"   // Avoids 1.9GB tmpfs limit\n'
    '    }\n'
    '    steps {\n'
    '        sh "mkdir -p /var/lib/jenkins/trivy-cache /var/lib/jenkins/trivy-tmp"\n'
    '        script {\n'
    '            ["user-service","product-service",...].each { svc ->\n'
    '                sh "trivy image --exit-code 0 --severity CRITICAL,HIGH \\\n'
    '                    --no-progress --scanners vuln \\\n'
    '                    --cache-dir /var/lib/jenkins/trivy-cache ${svc}:${IMAGE_TAG}"\n'
    '            }\n'
    '        }\n'
    '    }\n'
    '}'
)

doc.add_paragraph()
heading('Stage 6: Push to AWS ECR', 2, (0x2E, 0x75, 0xB6))
code_block(
    '# Authenticate with ECR (uses Jenkins EC2 IAM role — no credentials stored)\n'
    'aws ecr get-login-password --region us-east-1 \\\n'
    '  | docker login --username AWS --password-stdin ${ECR_URL}\n\n'
    '# Tag and push each service image\n'
    'docker tag user-service:${BUILD_NUMBER} ${ECR_URL}/user-service:${BUILD_NUMBER}\n'
    'docker push ${ECR_URL}/user-service:${BUILD_NUMBER}\n'
    '# ... repeated for all 6 services'
)

doc.add_paragraph()
heading('Stage 7: Update GitOps Config Repo', 2, (0x2E, 0x75, 0xB6))
para('This is the handoff from CI to CD — Jenkins updates image tags in the config repo:', size=11)
code_block(
    'git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/Chirag390/ecommerce-config.git config-repo\n\n'
    '# Update image tag in each service deployment.yaml\n'
    'sed -i "s|image: ${ECR_URL}/user-service:.*|image: ${ECR_URL}/user-service:${BUILD_NUMBER}|" \\\n'
    '    config-repo/k8s/user-service/deployment.yaml\n'
    '# ... for all 6 services\n\n'
    'git commit -m "CI: update all images to tag ${BUILD_NUMBER} [skip ci]"\n'
    'git push   # ArgoCD detects this commit and deploys'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  8. PHASE 5 — EKS SETUP
# ════════════════════════════════════════════════════════════════════════════

heading('8. Phase 5 — EKS Cluster Setup', 1, (0x1F, 0x4E, 0x79))

heading('8.1 Connect kubectl to EKS', 2, (0x2E, 0x75, 0xB6))
code_block(
    'aws eks update-kubeconfig --region us-east-1 --name devops-demo-cluster\n'
    'kubectl get nodes   # Should show 2 nodes in Ready state'
)

heading('8.2 EBS CSI Driver (for MongoDB persistent volume)', 2, (0x2E, 0x75, 0xB6))
para(
    'MongoDB uses a StatefulSet with a PersistentVolumeClaim backed by an AWS EBS volume. '
    'The EBS CSI Driver addon is required for Kubernetes to create EBS volumes automatically.',
    size=11
)
code_block(
    '# Install the EBS CSI Driver addon\n'
    'aws eks create-addon \\\n'
    '  --cluster-name devops-demo-cluster \\\n'
    '  --addon-name aws-ebs-csi-driver\n\n'
    '# IMPORTANT: Fix IMDS hop limit on worker nodes (required for addon to work in containers)\n'
    '# EBS CSI controller runs in a pod which needs to reach the EC2 metadata service\n'
    '# The default hop limit of 1 blocks this — must increase to 2\n'
    'aws ec2 modify-instance-metadata-options \\\n'
    '  --instance-id <NODE_INSTANCE_ID> \\\n'
    '  --http-put-response-hop-limit 2 \\\n'
    '  --http-endpoint enabled'
)

heading('8.3 MongoDB StatefulSet', 2, (0x2E, 0x75, 0xB6))
para('Key configuration for MongoDB with persistent storage:', size=11)
code_block(
    'apiVersion: apps/v1\n'
    'kind: StatefulSet\n'
    'metadata:\n'
    '  name: mongodb\n'
    '  namespace: ecommerce\n'
    'spec:\n'
    '  serviceName: mongodb\n'
    '  replicas: 1\n'
    '  template:\n'
    '    spec:\n'
    '      containers:\n'
    '        - name: mongodb\n'
    '          image: mongo:7.0\n'
    '          env:\n'
    '            - name: MONGO_INITDB_ROOT_USERNAME\n'
    '              valueFrom:\n'
    '                secretKeyRef: { name: mongodb-secret, key: username }\n'
    '  volumeClaimTemplates:\n'
    '    - metadata:\n'
    '        name: mongodb-storage\n'
    '      spec:\n'
    '        accessModes: ["ReadWriteOnce"]\n'
    '        storageClassName: gp2      # Must match EKS StorageClass\n'
    '        resources:\n'
    '          requests:\n'
    '            storage: 10Gi'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  9. PHASE 6 — ARGOCD GITOPS
# ════════════════════════════════════════════════════════════════════════════

heading('9. Phase 6 — ArgoCD GitOps CD', 1, (0x1F, 0x4E, 0x79))

heading('9.1 Install ArgoCD', 2, (0x2E, 0x75, 0xB6))
code_block(
    'kubectl create namespace argocd\n\n'
    'kubectl apply -n argocd \\\n'
    '  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml\n\n'
    '# Expose ArgoCD UI via LoadBalancer\n'
    'kubectl patch svc argocd-server -n argocd \\\n'
    '  -p \'{"spec":{"type":"LoadBalancer"}}\'\n\n'
    '# Get initial admin password\n'
    'kubectl -n argocd get secret argocd-initial-admin-secret \\\n'
    '  -o jsonpath="{.data.password}" | base64 -d'
)

heading('9.2 ArgoCD Application Manifest', 2, (0x2E, 0x75, 0xB6))
code_block(
    'apiVersion: argoproj.io/v1alpha1\n'
    'kind: Application\n'
    'metadata:\n'
    '  name: ecommerce-app\n'
    '  namespace: argocd\n'
    'spec:\n'
    '  source:\n'
    '    repoURL: https://github.com/Chirag390/ecommerce-config.git\n'
    '    targetRevision: main\n'
    '    path: k8s\n'
    '    directory:\n'
    '      recurse: true     # Scans k8s/user-service/, k8s/product-service/, etc.\n'
    '  destination:\n'
    '    server: https://kubernetes.default.svc\n'
    '    namespace: ecommerce\n'
    '  syncPolicy:\n'
    '    automated:\n'
    '      prune: true       # Deletes K8s resources removed from git\n'
    '      selfHeal: true    # Reverts manual kubectl changes back to git state\n'
    '    syncOptions:\n'
    '      - CreateNamespace=true'
)

para(
    'selfHeal: true is a powerful GitOps principle — if anyone manually edits a deployment '
    'via kubectl, ArgoCD detects the drift and reverts it within minutes to match the git state.',
    size=11
)

heading('9.3 GitOps Flow Explained', 2, (0x2E, 0x75, 0xB6))
add_table(
    ['Step', 'What Happens', 'Who Does It'],
    [
        ['1', 'Developer pushes code to ecommerce-app repo',                                   'Developer'],
        ['2', 'Jenkins pipeline runs (build → test → scan → push to ECR)',                     'Jenkins (automated)'],
        ['3', 'Jenkins updates image tags in ecommerce-config repo',                           'Jenkins (automated)'],
        ['4', 'ArgoCD polls ecommerce-config every 3 minutes, detects new commit',             'ArgoCD (automated)'],
        ['5', 'ArgoCD computes diff between git manifests and live K8s state',                 'ArgoCD (automated)'],
        ['6', 'ArgoCD applies changed manifests (kubectl apply)',                               'ArgoCD (automated)'],
        ['7', 'Kubernetes pulls new images from ECR, performs rolling update',                 'Kubernetes (automated)'],
        ['8', 'Readiness probes verify new pods are healthy before old pods terminate',        'Kubernetes (automated)'],
        ['9', 'Zero-downtime deployment complete — new version is live',                       '(done)'],
    ],
    [0.5, 4.0, 2.0]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  10. PHASE 7 — MONITORING
# ════════════════════════════════════════════════════════════════════════════

heading('10. Phase 7 — Monitoring (Prometheus + Grafana)', 1, (0x1F, 0x4E, 0x79))

heading('10.1 Install kube-prometheus-stack', 2, (0x2E, 0x75, 0xB6))
code_block(
    'helm repo add prometheus-community \\\n'
    '  https://prometheus-community.github.io/helm-charts\n'
    'helm repo update\n\n'
    'helm install monitoring prometheus-community/kube-prometheus-stack \\\n'
    '  --namespace monitoring \\\n'
    '  --create-namespace \\\n'
    '  --set grafana.service.type=LoadBalancer\n\n'
    '# Get Grafana admin password\n'
    'kubectl get secret monitoring-grafana -n monitoring \\\n'
    '  -o jsonpath="{.data.admin-password}" | base64 -d'
)

heading('10.2 How Prometheus Auto-Discovers Services', 2, (0x2E, 0x75, 0xB6))
para(
    'Each Spring Boot deployment has pod annotations that tell Prometheus where to scrape metrics. '
    'No manual Prometheus config required:',
    size=11
)
code_block(
    'metadata:\n'
    '  annotations:\n'
    '    prometheus.io/scrape: "true"\n'
    '    prometheus.io/path:   "/actuator/prometheus"\n'
    '    prometheus.io/port:   "8081"'
)
para(
    'Spring Boot Actuator + Micrometer library automatically expose 200+ JVM and HTTP metrics '
    'at the /actuator/prometheus endpoint in Prometheus format.',
    size=11
)

heading('10.3 Grafana Dashboards Available', 2, (0x2E, 0x75, 0xB6))
add_table(
    ['Dashboard', 'Key Metrics Shown'],
    [
        ['Kubernetes / Compute Resources / Cluster', 'Total CPU%, Memory%, requests/limits per namespace'],
        ['Kubernetes / Compute Resources / Node (Pods)', 'Per-pod CPU, memory usage on each node'],
        ['Kubernetes / Networking / Pod', 'Network receive/transmit bandwidth per pod'],
        ['Kubernetes / Nodes', 'Node disk I/O, network, CPU, memory'],
        ['JVM (Micrometer)', 'Heap usage, GC pauses, thread count, HTTP error rates per service'],
    ],
    [2.5, 4.0]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  11. SCREENSHOTS
# ════════════════════════════════════════════════════════════════════════════

heading('11. Project Screenshots', 1, (0x1F, 0x4E, 0x79))

para('All screenshots taken from the live running system on AWS EKS.', size=11)
doc.add_paragraph()

heading('11.1 ShopEasy E-Commerce App (Live)', 2, (0x2E, 0x75, 0xB6))
para(
    'The frontend is served by Nginx running in an EKS pod, accessible via an AWS Classic Load Balancer. '
    'It shows real product data fetched from product-service through the API gateway and MongoDB.',
    size=11
)
add_image('screenshots/app-frontend.png',
          'Fig 1: ShopEasy frontend running live on AWS EKS — MacBook Pro, iPhone 15, headphones, Nike shoes seeded by product-service')

doc.add_paragraph()
heading('11.2 Grafana — Kubernetes Cluster Overview', 2, (0x2E, 0x75, 0xB6))
para(
    'The Cluster dashboard shows the aggregate view across all namespaces. '
    'CPU utilisation is 4.96% — the cluster is healthy and has headroom. '
    'Memory limits at 95.4% reflect the resource requests set in deployment.yaml files.',
    size=11
)
add_image('screenshots/grafana-cluster.png',
          'Fig 2: Grafana Cluster dashboard — 4 namespaces, CPU 4.96%, Memory 47.9%')

doc.add_paragraph()
heading('11.3 Grafana — Node / Pod CPU Usage', 2, (0x2E, 0x75, 0xB6))
para(
    'The Node (Pods) dashboard breaks down CPU consumption per pod. '
    'The spike at 21:40 represents the moment all services came online after the EBS CSI fix. '
    'Node has 2 vCPU capacity (max capacity line = 2).',
    size=11
)
add_image('screenshots/grafana-node-pods.png',
          'Fig 3: Grafana Node/Pods dashboard — per-pod CPU breakdown, mongodb-0 and argocd pods visible')

doc.add_paragraph()
heading('11.4 Grafana — Kubernetes Pod Networking', 2, (0x2E, 0x75, 0xB6))
para(
    'The Networking dashboard shows real-time bandwidth for the aws-node pod (VPC CNI). '
    '314 kb/s receive and 369 kb/s transmit reflects inter-pod communication across the cluster.',
    size=11
)
add_image('screenshots/grafana-networking.png',
          'Fig 4: Grafana Networking dashboard — aws-node pod: 314 kb/s receive, 369 kb/s transmit')

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  12. MICROSERVICES ARCHITECTURE
# ════════════════════════════════════════════════════════════════════════════

heading('12. Microservices Architecture', 1, (0x1F, 0x4E, 0x79))

add_table(
    ['Service', 'Port', 'Tech', 'Key Endpoints', 'Database'],
    [
        ['user-service',         '8081', 'Spring Boot 3.2', 'POST /api/users/register, POST /api/users/login',             'userdb (MongoDB)'],
        ['product-service',      '8082', 'Spring Boot 3.2', 'GET /api/products, PUT /api/products/{id}/stock/reduce',       'productdb (MongoDB)'],
        ['order-service',        '8083', 'Spring Boot 3.2', 'POST /api/orders, GET /api/orders/user/{userId}',              'orderdb (MongoDB)'],
        ['notification-service', '8084', 'Spring Boot 3.2', 'POST /api/notifications, GET /api/notifications/{userId}',    'notificationdb (MongoDB)'],
        ['api-gateway',          '8080', 'Spring Cloud Gateway', 'Routes /api/** to correct microservice, adds CORS',      '—'],
        ['frontend',             '80',   'Nginx + JS',      'Serves ShopEasy HTML/CSS/JS, proxies /api/ to api-gateway',   '—'],
        ['mongodb',              '27017','MongoDB 7.0',     'StatefulSet, 10Gi EBS PVC, credentials from K8s Secret',      '4 databases'],
    ],
    [1.5, 0.6, 1.5, 2.5, 1.5]
)

doc.add_paragraph()
para('Inter-service communication flow (for placing an order):', bold=True, size=11)
code_block(
    'User clicks "Buy Now" in browser\n'
    '    → POST /api/orders to api-gateway:8080\n'
    '    → api-gateway routes to order-service:8083\n'
    '    → order-service calls product-service:8082 to reduce stock\n'
    '    → order-service calls notification-service:8084 to create alert\n'
    '    → order-service saves order to orderdb in MongoDB\n'
    '    → 200 OK returned to browser'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  13. TROUBLESHOOTING
# ════════════════════════════════════════════════════════════════════════════

heading('13. Key Issues Encountered & Fixes', 1, (0x1F, 0x4E, 0x79))

para(
    'Real-world DevOps projects always hit problems. These were the significant issues '
    'encountered during this project and how they were resolved.',
    size=11
)
doc.add_paragraph()

add_table(
    ['Issue', 'Root Cause', 'Fix Applied'],
    [
        ['EKS 1.29 AMI not found',                  'AWS removed AL2 AMIs for EKS 1.29',                        'Upgraded to EKS 1.32 in eks.tf'],
        ['SonarQube EC2 disk too small (20GB)',      'AL2023 snapshot minimum is 30GB',                          'Changed EBS volume to 30GB in Terraform'],
        ['parallel() not allowed in Jenkins',        'parallel() inside withSonarQubeEnv needs script block',    'Wrapped in script {} block in Jenkinsfile'],
        ['Jenkins Quality Gate hangs forever',       'SonarQube webhook not configured',                        'Added webhook in SonarQube pointing to Jenkins'],
        ['Trivy cache file lock errors',             'Parallel Trivy scans share cache — race condition',        'Changed Trivy from parallel to sequential'],
        ['Trivy: No space left on device',           'Trivy tmpfiles wrote to 1.9GB tmpfs',                     'Added TMPDIR=/var/lib/jenkins/trivy-tmp env var'],
        ['MongoDB PVC stuck in Pending',             'No StorageClass specified — EBS CSI needs explicit gp2',   'Added storageClassName: gp2 to StatefulSet'],
        ['EBS CSI pod CrashLoopBackOff',             'EC2 IMDS hop limit=1 blocks containerized metadata calls', 'aws ec2 modify-instance-metadata-options --http-put-response-hop-limit 2'],
        ['Services CrashLoopBackOff after MongoDB',  'Services started before MongoDB was ready',               'kubectl rollout restart deployment user-service product-service'],
        ['ArgoCD only synced Namespace',             'directory.recurse missing — only root k8s/ scanned',       'Added directory.recurse: true to application.yaml'],
        ['Monitoring pods Pending',                  'Node had too many pods (EKS t3.medium limit hit)',         'Scaled ecommerce services from 2 to 1 replica'],
    ],
    [1.8, 2.2, 2.5]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  14. KEY DEVOPS CONCEPTS
# ════════════════════════════════════════════════════════════════════════════

heading('14. Key DevOps Concepts Demonstrated', 1, (0x1F, 0x4E, 0x79))

add_table(
    ['Concept', 'How It Is Implemented in This Project'],
    [
        ['Infrastructure as Code',      'Terraform manages all AWS resources — VPC, EC2, EKS, ECR, IAM. Zero manual console clicks.'],
        ['Configuration as Code',       'Jenkinsfile in git defines the entire CI pipeline. Anyone can reproduce it by cloning the repo.'],
        ['GitOps',                      'ArgoCD watches ecommerce-config repo. Git is the single source of truth for production state.'],
        ['Immutable Infrastructure',    'Docker images are never patched. Every change = new image tag = new deployment. Old images kept in ECR.'],
        ['Shift Left Security',         'Trivy scans happen at build time (before deployment), not in production where fixing is expensive.'],
        ['Quality Gates',               'SonarQube blocks code that fails quality checks from ever reaching a Docker image or deployment.'],
        ['Zero Downtime Deployments',   'Kubernetes rolling updates: new pods start before old ones stop. Readiness probes control traffic.'],
        ['Separation of Concerns',      'Two repos: source code triggers CI. Config repo triggers CD. Clean boundary between build and deploy.'],
        ['Observability',               'Prometheus scrapes 200+ metrics per service. Grafana provides cluster, node, pod, and JVM dashboards.'],
        ['Microservices',               '4 independent services + gateway + frontend. Each has its own database, Docker image, and deployment.'],
        ['Least Privilege IAM',         'Jenkins EC2 uses IAM instance role instead of stored AWS credentials — no secret keys on disk.'],
        ['Persistent Storage',          'MongoDB uses StatefulSet + EBS PVC. Data survives pod restarts and node replacements.'],
    ],
    [2.0, 4.5]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  15. REPRODUCE THIS PROJECT
# ════════════════════════════════════════════════════════════════════════════

heading('15. How to Reproduce This Project', 1, (0x1F, 0x4E, 0x79))

steps = [
    ('Clone repos',
     'git clone https://github.com/Chirag390/ecommerce-app.git\n'
     'git clone https://github.com/Chirag390/ecommerce-config.git'),
    ('Create EC2 key pair',
     'aws ec2 create-key-pair --key-name devops-key --query "KeyMaterial" --output text > devops-key.pem\n'
     'chmod 400 devops-key.pem'),
    ('Provision infrastructure with Terraform',
     'cd ecommerce-app/terraform && terraform init && terraform apply'),
    ('Install software on Jenkins EC2',
     'SSH in and install: Java 21, Jenkins, Docker, Maven, AWS CLI, kubectl, Trivy'),
    ('Configure Jenkins',
     'Install plugins, add GitHub + SonarQube credentials, configure SonarQube server, create pipeline job'),
    ('Start SonarQube on SonarQube EC2',
     'docker run -d -p 9000:9000 sonarqube:lts-community\nAdd Jenkins webhook in SonarQube UI'),
    ('Set up EKS',
     'aws eks update-kubeconfig --region us-east-1 --name devops-demo-cluster\n'
     'aws eks create-addon --cluster-name devops-demo-cluster --addon-name aws-ebs-csi-driver\n'
     'Increase IMDS hop limit to 2 on worker nodes'),
    ('Install ArgoCD',
     'kubectl create namespace argocd\n'
     'kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml\n'
     'kubectl apply -f ecommerce-config/argocd/application.yaml'),
    ('Trigger Jenkins pipeline',
     'Push a commit to ecommerce-app → Jenkins builds, scans, pushes to ECR, updates config repo → ArgoCD deploys'),
    ('Install Prometheus + Grafana',
     'helm repo add prometheus-community https://prometheus-community.github.io/helm-charts\n'
     'helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --set grafana.service.type=LoadBalancer'),
    ('Access the app',
     'kubectl get svc frontend -n ecommerce   # Get LoadBalancer URL\n'
     'kubectl get svc monitoring-grafana -n monitoring   # Get Grafana URL'),
]

for i, (title_text, cmd) in enumerate(steps, 1):
    heading(f'Step {i}: {title_text}', 2, (0x2E, 0x75, 0xB6))
    code_block(cmd)
    doc.add_paragraph()

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
#  16. REPO LINKS & AUTHOR
# ════════════════════════════════════════════════════════════════════════════

heading('16. Repository Links', 1, (0x1F, 0x4E, 0x79))

add_table(
    ['Repo', 'URL', 'Contents'],
    [
        ['ecommerce-app',    'https://github.com/Chirag390/ecommerce-app',    'Application source code, Jenkinsfile, Dockerfiles, Terraform'],
        ['ecommerce-config', 'https://github.com/Chirag390/ecommerce-config', 'Kubernetes manifests, ArgoCD application.yaml'],
    ],
    [1.5, 3.0, 2.0]
)

doc.add_paragraph()
heading('Author', 1, (0x1F, 0x4E, 0x79))
para('Chirag Goyal', bold=True, size=14)
para('End-to-End DevOps Project — April 2026', size=11)
para(
    'This project was built from scratch as a hands-on learning exercise covering '
    'the complete DevOps lifecycle: infrastructure provisioning, CI/CD pipeline design, '
    'container orchestration, GitOps deployment, and production monitoring.',
    size=11
)

# ── Save ────────────────────────────────────────────────────────────────────
output_path = r'c:\Users\Chirag Goyal\Desktop\New folder\ecommerce-app\ShopEasy_DevOps_Project.docx'
doc.save(output_path)
print(f'Document saved: {output_path}')
