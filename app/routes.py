from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Course, Module, Enrollment, UserProgress, User
from app.forms import CourseForm
from sqlalchemy import or_
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

# Sample AWS course data - COMPLETE WITH REAL CONTENT AND MINI-TUTORIALS
AWS_COURSES_DATA = [
    {
        'title': 'AWS Fundamentals for Beginners',
        'slug': 'aws-fundamentals',
        'description': 'Master the core AWS services and concepts. Learn about compute, storage, databases, networking, and security.',
        'difficulty': 'beginner',
        'duration': 12,
        'modules': [
            {
                'title': 'Introduction to Cloud Computing & AWS',
                'content': '''
                <h3>What is Cloud Computing?</h3>
                <p>Cloud computing is the on-demand delivery of IT resources over the Internet with pay-as-you-go pricing.</p>
                
                <h4>AWS Global Infrastructure</h4>
                <ul>
                    <li><strong>Regions</strong>: 32 geographic regions worldwide (e.g., us-east-1, eu-west-1)</li>
                    <li><strong>Availability Zones (AZs)</strong>: 102 AZs - isolated locations within regions</li>
                    <li><strong>Edge Locations</strong>: 400+ points of presence for CloudFront and Route 53</li>
                </ul>
                
                <h4>AWS Shared Responsibility Model</h4>
                <p><strong>AWS Responsibility</strong>: Security OF the Cloud (infrastructure, hardware, software)</p>
                <p><strong>Customer Responsibility</strong>: Security IN the Cloud (data, applications, identity management)</p>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Check AWS Region</h5>
                    <pre><code class="language-bash">
# List all available regions
aws ec2 describe-regions --query "Regions[].RegionName" --output table
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Cloud Computing & AWS - Quick Start

### 📖 **What You'll Learn:**
- Core concepts of cloud computing
- AWS global infrastructure (Regions, AZs, Edge Locations)
- AWS Shared Responsibility Model
- Setting up your AWS account

### 🔑 **Key Concepts:**
1. **Cloud Computing**: On-demand IT resources over the internet
2. **AWS Regions**: 32 geographic areas worldwide
3. **Availability Zones (AZs)**: Isolated data centers within regions
4. **Shared Responsibility**: AWS secures the cloud, you secure in the cloud

### 🏗️ **AWS Infrastructure Map:**
Global Infrastructure:
├── Regions (e.g., us-east-1, eu-west-1)
│ ├── Availability Zones (2-6 per region)
│ └── Edge Locations (400+ for CDN/DNS)

text

### ⚠️ **Common Beginner Mistakes:**
- Using root account for daily operations ❌
- Not enabling MFA on root account ❌
- Ignoring cost monitoring ❌
- Creating resources in wrong region ❌

### ✅ **First Day Checklist:**
1. ✅ Create IAM user (don't use root)
2. ✅ Enable MFA on root and IAM users
3. ✅ Set up billing alerts
4. ✅ Choose correct region for resources
5. ✅ Explore AWS Free Tier limits

### 💡 **Pro Tips:**
- Start with us-east-1 for tutorials (most services available)
- Use AWS Organizations for multiple accounts
- Enable CloudTrail for audit logging
- Tag all resources for cost allocation'''
            },
            {
                'title': 'IAM - Identity and Access Management',
                'content': '''
                <h3>IAM Fundamentals</h3>
                <p>IAM is the authentication and authorization service for AWS resources.</p>
                
                <h4>Key Concepts:</h4>
                <ul>
                    <li><strong>Users</strong>: End users (people or applications)</li>
                    <li><strong>Groups</strong>: Collection of users with similar permissions</li>
                    <li><strong>Roles</strong>: Temporary permissions for AWS services or users</li>
                    <li><strong>Policies</strong>: JSON documents defining permissions (managed or inline)</li>
                </ul>
                
                <h4>Best Practices:</h4>
                <ol>
                    <li>Follow the principle of least privilege</li>
                    <li>Use IAM roles instead of access keys when possible</li>
                    <li>Enable MFA for root and IAM users</li>
                    <li>Regularly rotate credentials</li>
                </ol>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create IAM User</h5>
                    <pre><code class="language-bash">
# Create IAM user
aws iam create-user --user-name CloudAdmin

# Attach administrator policy
aws iam attach-user-policy --user-name CloudAdmin \\
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access keys
aws iam create-access-key --user-name CloudAdmin
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 IAM - Your Security Foundation

### 📖 **What You'll Learn:**
- IAM users, groups, roles, and policies
- Principle of Least Privilege
- Multi-Factor Authentication (MFA)
- Best practices for IAM security

### 🔑 **IAM Components:**
1. **Users**: People or applications (never use root!)
2. **Groups**: Collections of users with similar permissions
3. **Roles**: Temporary permissions for services/users
4. **Policies**: JSON documents defining permissions

### 🏗️ **IAM Best Practice Architecture:**
IAM Users → IAM Groups → IAM Policies
↓
IAM Roles → AWS Services
↓
MFA Required

text

### ⚠️ **Critical Security Mistakes:**
- Sharing access keys ❌
- Using wildcard permissions (*) ❌
- Not rotating credentials ❌
- Hardcoding secrets in code ❌

### ✅ **IAM Security Checklist:**
1. ✅ Create individual IAM users
2. ✅ Use groups to assign permissions
3. ✅ Grant least privilege access
4. ✅ Configure strong password policy
5. ✅ Enable MFA for privileged users
6. ✅ Use roles for EC2 applications
7. ✅ Rotate access keys regularly

### 🔐 **Policy Example (Least Privilege):**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::bucket-name/*"
}
```'''
            },
            {
                'title': 'EC2 - Elastic Compute Cloud',
                'content': '''
                <h3>EC2: Virtual Servers in the Cloud</h3>
                <p>EC2 provides resizable compute capacity in the cloud.</p>
                
                <h4>EC2 Instance Types:</h4>
                <table class="table table-bordered">
                    <thead>
                        <tr><th>Family</th><th>Purpose</th><th>Example</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>t3/t4g</td><td>General purpose, burstable</td><td>Web servers, small databases</td></tr>
                        <tr><td>m5/m6g</td><td>General purpose</td><td>Application servers</td></tr>
                        <tr><td>c5/c6g</td><td>Compute optimized</td><td>Batch processing, gaming</td></tr>
                        <tr><td>r5/r6g</td><td>Memory optimized</td><td>In-memory databases, caching</td></tr>
                    </tbody>
                </table>
                
                <h4>Launch an EC2 Instance:</h4>
                <ol>
                    <li>Choose AMI (Amazon Machine Image)</li>
                    <li>Select instance type</li>
                    <li>Configure network (VPC, subnet)</li>
                    <li>Add storage (EBS volumes)</li>
                    <li>Configure security group</li>
                    <li>Review and launch</li>
                </ol>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Launch EC2 Instance via CLI</h5>
                    <pre><code class="language-bash">
# Launch Ubuntu 22.04 instance
aws ec2 run-instances \\
    --image-id ami-0c55b159cbfafe1f0 \\
    --instance-type t2.micro \\
    --key-name MyKeyPair \\
    --security-group-ids sg-12345678 \\
    --subnet-id subnet-abcdefgh \\
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=WebServer}]'
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 EC2 - Virtual Servers Made Easy

### 📖 **What You'll Learn:**
- Launching and configuring EC2 instances
- Understanding instance types and families
- Working with AMIs and EBS volumes
- Security groups and key pairs

### 🔑 **EC2 Instance Families:**
- **General Purpose (t3, m5)**: Web servers, small databases
- **Compute Optimized (c5)**: Batch processing, gaming
- **Memory Optimized (r5)**: In-memory databases, caching
- **Storage Optimized (i3)**: NoSQL databases, data warehousing

### 🏗️ **Launching an EC2 Instance:**
Choose AMI (Amazon Machine Image)

Select Instance Type (t2.micro for Free Tier)

Configure Instance (VPC, subnet, IAM role)

Add Storage (EBS volumes)

Configure Security Group (firewall rules)

Review and Launch

Create/Select Key Pair

text

### ⚠️ **Common EC2 Mistakes:**
- Leaving instances running (cost!) ❌
- Using default security groups ❌
- Not monitoring instance health ❌
- Forgetting to terminate test instances ❌

### ✅ **EC2 Best Practices:**
1. ✅ Use instance metadata for configuration
2. ✅ Implement auto-scaling for variable workloads
3. ✅ Use placement groups for low latency
4. ✅ Enable termination protection for critical instances
5. ✅ Use Elastic IPs sparingly (they cost when not attached)

### 💰 **Cost Optimization:**
- Use Spot Instances for fault-tolerant workloads
- Reserve instances for steady-state workloads
- Right-size instances based on utilization
- Use auto-scaling to match demand'''
            },
            {
                'title': 'S3 - Simple Storage Service',
                'content': '''
                <h3>S3: Object Storage Service</h3>
                <p>S3 provides scalable, durable object storage with 99.999999999% (11 9s) durability.</p>
                
                <h4>S3 Storage Classes:</h4>
                <ul>
                    <li><strong>S3 Standard</strong>: Frequently accessed data (default)</li>
                    <li><strong>S3 Intelligent-Tiering</strong>: Automatic cost optimization</li>
                    <li><strong>S3 Standard-IA</strong>: Infrequently accessed</li>
                    <li><strong>S3 Glacier</strong>: Archive storage (minutes to hours retrieval)</li>
                    <li><strong>S3 Glacier Deep Archive</strong>: Lowest cost (12+ hours retrieval)</li>
                </ul>
                
                <h4>S3 Features:</h4>
                <ul>
                    <li><strong>Versioning</strong>: Keep multiple versions of objects</li>
                    <li><strong>Lifecycle Policies</strong>: Automate transition between storage classes</li>
                    <li><strong>Replication</strong>: Cross-region or same-region</li>
                    <li><strong>Encryption</strong>: SSE-S3, SSE-KMS, SSE-C, client-side</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> S3 Basic Operations</h5>
                    <pre><code class="language-bash">
# Create bucket (unique name globally)
aws s3 mb s3://my-unique-bucket-name-2024

# Upload file
aws s3 cp file.txt s3://my-unique-bucket-name-2024/

# Sync directory
aws s3 sync ./my-folder s3://my-unique-bucket-name-2024/my-folder/

# Enable versioning
aws s3api put-bucket-versioning \\
    --bucket my-unique-bucket-name-2024 \\
    --versioning-configuration Status=Enabled
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 S3 - Unlimited Object Storage

### 📖 **What You'll Learn:**
- S3 buckets and objects fundamentals
- Storage classes and lifecycle policies
- Security, encryption, and versioning
- S3 features for data lakes and static websites

### 🔑 **S3 Storage Classes:**
1. **S3 Standard**: Frequently accessed data
2. **S3 Intelligent-Tiering**: Automatic cost optimization
3. **S3 Standard-IA**: Infrequently accessed
4. **S3 Glacier**: Archive storage (minutes retrieval)
5. **S3 Glacier Deep Archive**: Lowest cost (12+ hours retrieval)

### 🏗️ **S3 Data Lake Structure:**
s3://my-data-lake/
├── raw/ (original data)
├── processed/ (cleaned data)
├── curated/ (business-ready)
└── sandbox/ (experimental)

text

### ⚠️ **Critical S3 Mistakes:**
- Public buckets without need ❌
- No versioning enabled ❌
- No lifecycle policies ❌
- Wrong storage class for access patterns ❌

### ✅ **S3 Security & Best Practices:**
1. ✅ **Always enable encryption** (SSE-S3 minimum)
2. ✅ **Use bucket policies** for fine-grained access
3. ✅ **Enable versioning** for critical data
4. ✅ **Set up lifecycle rules** for cost optimization
5. ✅ **Enable MFA Delete** for production buckets
6. ✅ **Use S3 Access Logs** for auditing
7. ✅ **Configure Cross-Region Replication** for DR

### 🌐 **Static Website Hosting:**
Enable website hosting
aws s3 website s3://bucket-name --index-document index.html

Set bucket policy for public read
{
"Effect": "Allow",
"Principal": "*",
"Action": "s3:GetObject",
"Resource": "arn:aws:s3:::bucket-name/*"
}

'''
            },
            {
                'title': 'RDS - Relational Database Service',
                'content': '''
                <h3>RDS: Managed Relational Databases</h3>
                <p>RDS makes it easy to set up, operate, and scale relational databases in the cloud.</p>
                
                <h4>Supported Database Engines:</h4>
                <ul>
                    <li>Amazon Aurora (MySQL/PostgreSQL compatible)</li>
                    <li>PostgreSQL</li>
                    <li>MySQL</li>
                    <li>MariaDB</li>
                    <li>Oracle</li>
                    <li>Microsoft SQL Server</li>
                </ul>
                
                <h4>RDS Features:</h4>
                <ul>
                    <li><strong>Multi-AZ Deployment</strong>: High availability across AZs</li>
                    <li><strong>Read Replicas</strong>: Scale read operations</li>
                    <li><strong>Automated Backups</strong>: Point-in-time recovery</li>
                    <li><strong>Storage Auto-scaling</strong>: Automatically increase storage</li>
                    <li><strong>Performance Insights</strong>: Database performance monitoring</li>
                </ul>
                
                <div class="tips mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
                    <h5><i class="fas fa-lightbulb"></i> Pro Tip: RDS Best Practices</h5>
                    <ul>
                        <li>Use Multi-AZ for production databases</li>
                        <li>Enable deletion protection for critical databases</li>
                        <li>Monitor FreeStorageSpace metric (keep above 10%)</li>
                        <li>Use parameter groups for database tuning</li>
                    </ul>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 RDS - Managed Databases Simplified

### 📖 **What You'll Learn:**
- Setting up and managing RDS instances
- Multi-AZ deployments for high availability
- Read replicas for scaling reads
- Backup, restoration, and monitoring

### 🔑 **Supported Database Engines:**
- **Amazon Aurora** (MySQL/PostgreSQL compatible) ⭐
- **PostgreSQL** (open source, feature-rich)
- **MySQL** (most popular open source)
- **MariaDB** (MySQL fork)
- **Oracle** (enterprise workloads)
- **SQL Server** (Microsoft ecosystem)

### 🏗️ **RDS High Availability Architecture:**
Primary DB (AZ1) → Standby DB (AZ2) [Synchronous replication]
↓
Read Replica (AZ3) [Asynchronous replication]
↓
Application Servers

text

### ⚠️ **Database Management Mistakes:**
- Not using Multi-AZ for production ❌
- Publicly accessible databases ❌
- No monitoring on storage/CPU ❌
- Not testing backups regularly ❌

### ✅ **RDS Best Practices:**
1. ✅ **Use Multi-AZ** for production databases
2. ✅ **Enable deletion protection** for critical DBs
3. ✅ **Monitor FreeStorageSpace** (keep >10%)
4. ✅ **Use parameter groups** for performance tuning
5. ✅ **Implement read replicas** for read-heavy workloads
6. ✅ **Enable automated backups** with proper retention
7. ✅ **Use Performance Insights** for query optimization

### 🔒 **Security Considerations:**
- Use IAM database authentication when possible
- Encrypt RDS instances at rest
- Use security groups (not network ACLs) for DB access
- Rotate master passwords regularly
- Enable CloudWatch alarms for security events

### 💰 **Cost Optimization:**
- Right-size instance types based on workload
- Use reserved instances for steady workloads
- Delete old snapshots and automated backups
- Monitor storage auto-scaling to prevent surprises'''
            }
        ]
    },
    {
        'title': 'AWS Networking Deep Dive',
        'slug': 'aws-networking',
        'description': 'Master VPC, subnets, routing, security groups, and network connectivity in AWS.',
        'difficulty': 'intermediate',
        'duration': 16,
        'modules': [
            {
                'title': 'VPC Fundamentals',
                'content': '''
                <h3>Virtual Private Cloud (VPC)</h3>
                <p>A logically isolated section of the AWS Cloud where you can launch AWS resources.</p>
                
                <h4>VPC Components:</h4>
                <ul>
                    <li><strong>Subnets</strong>: Segment of VPC IP address range (public/private)</li>
                    <li><strong>Route Tables</strong>: Control traffic between subnets</li>
                    <li><strong>Internet Gateway (IGW)</strong>: Connect VPC to internet</li>
                    <li><strong>NAT Gateway</strong>: Allow private instances to access internet</li>
                    <li><strong>Security Groups</strong>: Stateful firewall at instance level</li>
                    <li><strong>Network ACLs</strong>: Stateless firewall at subnet level</li>
                </ul>
                
                <h4>Default vs Custom VPC:</h4>
                <ul>
                    <li><strong>Default VPC</strong>: Created in each region automatically
                        <ul>
                            <li>Has internet gateway attached</li>
                            <li>Subnets have route to IGW</li>
                            <li>Designed for quick start</li>
                        </ul>
                    </li>
                    <li><strong>Custom VPC</strong>: Created by user with full control
                        <ul>
                            <li>Define own IP range (CIDR)</li>
                            <li>Configure subnets, routing</li>
                            <li>Better for production</li>
                        </ul>
                    </li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create VPC with Subnets</h5>
                    <pre><code class="language-bash">
# Create VPC with CIDR 10.0.0.0/16
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create public subnet (10.0.1.0/24)
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.1.0/24

# Create private subnet (10.0.2.0/24)
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.2.0/24

# Create internet gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-12345678 --internet-gateway-id igw-abcdefgh
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 VPC - Your Private AWS Network

### 📖 **What You'll Learn:**
- VPC concepts and components
- Subnet design (public vs private)
- Internet and NAT gateways
- Route tables and network ACLs

### 🔑 **VPC Core Components:**
1. **Subnets**: IP ranges within VPC (public/private)
2. **Route Tables**: Traffic direction rules
3. **Internet Gateway (IGW)**: VPC ↔ Internet
4. **NAT Gateway**: Private subnet → Internet (outbound)
5. **Security Groups**: Instance-level firewall (stateful)
6. **Network ACLs**: Subnet-level firewall (stateless)

### 🏗️ **VPC Design Pattern:**
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)
│ ├── Internet Gateway
│ ├── NAT Gateway
│ └── Web Servers
└── Private Subnet (10.0.2.0/24)
├── Route to NAT Gateway
└── Databases (RDS)

text

### ⚠️ **Common VPC Mistakes:**
- CIDR range overlaps between VPCs ❌
- Forgetting route table associations ❌
- Public subnets for databases ❌
- Not using VPC Flow Logs for monitoring ❌

### ✅ **VPC Best Practices:**
1. ✅ Use /16 CIDR for VPC (65,536 IPs)
2. ✅ Create public and private subnets across AZs
3. ✅ Use NAT Gateway in public subnet for private instances
4. ✅ Enable VPC Flow Logs for security monitoring
5. ✅ Use security groups (not NACLs) when possible
6. ✅ Implement VPC endpoints for AWS services

### 🔧 **Creating a VPC:**
```bash
# Create VPC with CIDR block
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24

# Create Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx

# Update route table
aws ec2 create-route --route-table-id rtb-xxx \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-xxx
```'''
            },
            {
                'title': 'Security Groups & Network ACLs',
                'content': '''
                <h3>Network Security in AWS</h3>
                
                <h4>Security Groups (Stateful):</h4>
                <ul>
                    <li>Operate at instance level</li>
                    <li>ALLOW rules only (implicit deny)</li>
                    <li>Stateful: Return traffic automatically allowed</li>
                    <li>Can reference other security groups</li>
                    <li>Evaluated before Network ACLs</li>
                </ul>
                
                <h4>Network ACLs (Stateless):</h4>
                <ul>
                    <li>Operate at subnet level</li>
                    <li>ALLOW and DENY rules</li>
                    <li>Stateless: Return traffic must be explicitly allowed</li>
                    <li>Rules evaluated in order (lowest rule number first)</li>
                    <li>Default NACL allows all traffic</li>
                </ul>
                
                <h4>Comparison:</h4>
                <table class="table table-bordered">
                    <thead>
                        <tr><th>Aspect</th><th>Security Groups</th><th>Network ACLs</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Level</td><td>Instance level</td><td>Subnet level</td></tr>
                        <tr><td>Rules</td><td>Allow only</td><td>Allow/Deny</td></tr>
                        <tr><td>State</td><td>Stateful</td><td>Stateless</td></tr>
                        <tr><td>Order</td><td>All rules evaluated</td><td>Rule number order</td></tr>
                    </tbody>
                </table>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create Security Group</h5>
                    <pre><code class="language-bash">
# Create security group for web server
aws ec2 create-security-group \\
    --group-name WebServerSG \\
    --description "Security group for web servers" \\
    --vpc-id vpc-12345678

# Allow HTTP (port 80) from anywhere
aws ec2 authorize-security-group-ingress \\
    --group-id sg-abcdefgh \\
    --protocol tcp \\
    --port 80 \\
    --cidr 0.0.0.0/0

# Allow SSH (port 22) from your IP only
aws ec2 authorize-security-group-ingress \\
    --group-id sg-abcdefgh \\
    --protocol tcp \\
    --port 22 \\
    --cidr 203.0.113.0/24
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Network Security: SG vs NACL

### 📖 **What You'll Learn:**
- Security Groups (stateful firewall)
- Network ACLs (stateless firewall)
- When to use each
- Best practices for network security

### 🔑 **Security Groups (Stateful):**
- **Level**: Instance level
- **Rules**: Allow only (implicit deny)
- **State**: Stateful (return traffic auto-allowed)
- **Best for**: EC2 instances, RDS, Lambda

### 🔑 **Network ACLs (Stateless):**
- **Level**: Subnet level
- **Rules**: Allow/Deny
- **State**: Stateless (return traffic must be allowed)
- **Best for**: Subnet-wide rules, extra security layer

### 🏗️ **Security Architecture:**
Incoming Request:
Internet → Network ACL (subnet level) → Security Group (instance level) → EC2 Instance
↓ ↓
Stateless filter Stateful firewall

text

### ⚠️ **Security Mistakes:**
- Using NACLs when SGs suffice ❌
- Not using security group references ❌
- Open ports to 0.0.0.0/0 unnecessarily ❌
- Forgetting return paths in NACLs ❌

### ✅ **Security Best Practices:**
1. ✅ **Use Security Groups as primary defense**
2. ✅ **Use NACLs for subnet-wide deny rules**
3. ✅ **Reference security groups instead of IPs**
4. ✅ **Regularly review and clean up rules**
5. ✅ **Implement least privilege principle**
6. ✅ **Use VPC Flow Logs for traffic analysis**

### 🔐 **Example: Web Server Security Group**
```json
{
  "Inbound": [
    {"Protocol": "tcp", "Port": 80, "Source": "0.0.0.0/0"},
    {"Protocol": "tcp", "Port": 443, "Source": "0.0.0.0/0"},
    {"Protocol": "tcp", "Port": 22, "Source": "10.0.0.0/16"}
  ],
  "Outbound": [
    {"Protocol": "all", "Port": "all", "Destination": "0.0.0.0/0"}
  ]
}
```'''
            },
            {
                'title': 'VPC Peering and Endpoints',
                'content': '''
                <h3>VPC Connectivity Options</h3>
                
                <h4>VPC Peering:</h4>
                <p>Connect two VPCs privately using AWS network.</p>
                <ul>
                    <li>No transitive peering (A↔B and B↔C doesn't mean A↔C)</li>
                    <li>CIDR blocks must not overlap</li>
                    <li>Cross-region and cross-account peering supported</li>
                    <li>Update route tables in both VPCs</li>
                </ul>
                
                <h4>VPC Endpoints:</h4>
                <p>Private connectivity to AWS services without internet gateway.</p>
                <ul>
                    <li><strong>Interface Endpoints (PrivateLink)</strong>: ENI with private IP
                        <ul>
                            <li>Supported services: S3, DynamoDB, SNS, SQS, etc.</li>
                            <li>Cost: Hourly charge + data processing</li>
                        </ul>
                    </li>
                    <li><strong>Gateway Endpoints</strong>: Route table entry
                        <ul>
                            <li>Supported services: S3 and DynamoDB only</li>
                            <li>Free of charge</li>
                        </ul>
                    </li>
                </ul>
                
                <h4>When to Use:</h4>
                <ul>
                    <li><strong>VPC Peering</strong>: Connect VPCs for application communication</li>
                    <li><strong>Interface Endpoint</strong>: Access AWS services privately (most services)</li>
                    <li><strong>Gateway Endpoint</strong>: Access S3/DynamoDB privately (free option)</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create VPC Peering</h5>
                    <pre><code class="language-bash">
# Request VPC peering
aws ec2 create-vpc-peering-connection \\
    --vpc-id vpc-12345678 \\
    --peer-vpc-id vpc-87654321 \\
    --peer-region us-west-2

# Accept peering request (from peer VPC owner)
aws ec2 accept-vpc-peering-connection \\
    --vpc-peering-connection-id pcx-abcdefgh

# Add route in route table
aws ec2 create-route \\
    --route-table-id rtb-12345678 \\
    --destination-cidr-block 10.1.0.0/16 \\
    --vpc-peering-connection-id pcx-abcdefgh
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 VPC Connectivity Options

### 📖 **What You'll Learn:**
- VPC Peering for private VPC connections
- VPC Endpoints for AWS service access
- Choosing between peering and endpoints
- Route table configuration

### 🔑 **VPC Peering:**
- **Purpose**: Connect VPCs privately
- **Limitation**: No transitive peering
- **Requirement**: Non-overlapping CIDRs
- **Cost**: No data transfer cost within region

### 🔑 **VPC Endpoints:**
- **Gateway Endpoint**: S3/DynamoDB only (free)
- **Interface Endpoint**: All services (cost per hour)
- **Benefit**: No internet gateway needed
- **Security**: Private connectivity within VPC

### 🏗️ **When to Use Which:**
Application Communication → VPC Peering
↓
Access AWS Services → VPC Endpoints
↓
Choose:
├── S3/DynamoDB → Gateway Endpoint (free)
└── Other Services → Interface Endpoint

text

### ⚠️ **Connectivity Mistakes:**
- Expecting transitive peering ❌
- Overlapping CIDR ranges ❌
- Forgetting route table updates ❌
- Using IGW when endpoints available ❌

### ✅ **Best Practices:**
1. ✅ **Use VPC endpoints for AWS service access**
2. ✅ **Use VPC peering for multi-VPC applications**
3. ✅ **Implement route tables carefully**
4. ✅ **Monitor VPC endpoint costs**
5. ✅ **Use security groups with endpoints**

### 🔧 **VPC Endpoint Example:**
```bash
# Create S3 Gateway Endpoint
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxx \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-xxx \
    --vpc-endpoint-type Gateway
```'''
            },
            {
                'title': 'VPN and Direct Connect',
                'content': '''
                <h3>Hybrid Cloud Connectivity</h3>
                
                <h4>AWS Site-to-Site VPN:</h4>
                <ul>
                    <li>IPsec VPN connection over public internet</li>
                    <li>Virtual Private Gateway (VGW) on AWS side</li>
                    <li>Customer Gateway (CGW) on customer side</li>
                    <li>Setup time: Minutes</li>
                    <li>Bandwidth: Up to 1.25 Gbps per tunnel</li>
                    <li>Cost: VGW hourly charge + data transfer</li>
                </ul>
                
                <h4>AWS Direct Connect:</h4>
                <ul>
                    <li>Dedicated network connection to AWS</li>
                    <li>Private connectivity (bypasses public internet)</li>
                    <li>Consistent network performance</li>
                    <li>Setup time: Weeks (physical cross-connect)</li>
                    <li>Bandwidth: 1 Gbps or 10 Gbps ports</li>
                    <li>Cost: Port-hour charge + data transfer</li>
                </ul>
                
                <h4>Comparison:</h4>
                <table class="table table-bordered">
                    <thead>
                        <tr><th>Factor</th><th>Site-to-Site VPN</th><th>Direct Connect</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Setup Time</td><td>Minutes</td><td>Weeks</td></tr>
                        <tr><td>Connectivity</td><td>Over Internet</td><td>Dedicated Line</td></tr>
                        <tr><td>Performance</td><td>Variable</td><td>Consistent</td></tr>
                        <tr><td>Reliability</td><td>Internet dependent</td><td>99.9% SLA</td></tr>
                        <tr><td>Cost</td><td>Lower</td><td>Higher</td></tr>
                    </tbody>
                </table>
                
                <div class="tips mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
                    <h5><i class="fas fa-lightbulb"></i> Best Practice: VPN + Direct Connect</h5>
                    <p>Use Direct Connect as primary connection and VPN as backup (failover). This provides high availability for critical hybrid connections.</p>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Hybrid Cloud: VPN vs Direct Connect

### 📖 **What You'll Learn:**
- Site-to-Site VPN setup
- Direct Connect implementation
- Choosing between VPN and Direct Connect
- High availability strategies

### 🔑 **Site-to-Site VPN:**
- **Speed**: Setup in minutes
- **Cost**: Lower (pay per hour + data)
- **Performance**: Internet-dependent
- **Best for**: Temporary connections, PoCs

### 🔑 **Direct Connect:**
- **Speed**: Setup in weeks
- **Cost**: Higher (port charge + data)
- **Performance**: Consistent, dedicated
- **Best for**: Production, high-throughput

### 🏗️ **Hybrid Architecture:**
On-Premises Data Center
↓
├── Direct Connect (Primary)
└── VPN (Backup/Failover)
↓
AWS VPC

text

### ⚠️ **Hybrid Connectivity Mistakes:**
- Relying only on VPN for production ❌
- No failover strategy ❌
- Not monitoring connection health ❌
- Forgetting about data transfer costs ❌

### ✅ **Best Practices:**
1. ✅ **Use Direct Connect for production workloads**
2. ✅ **Implement VPN as backup/failover**
3. ✅ **Monitor connection metrics**
4. ✅ **Use Direct Connect Gateway for multi-region**
5. ✅ **Implement BGP for dynamic routing**

### 🛡️ **High Availability Setup:**
```bash
# Create Virtual Private Gateway
aws ec2 create-vpn-gateway --type ipsec.1

# Attach to VPC
aws ec2 attach-vpn-gateway \
    --vpc-id vpc-xxx \
    --vpn-gateway-id vgw-xxx

# Create Customer Gateway
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.12 \
    --bgp-asn 65000
```'''
            },
            {
                'title': 'Route 53 - DNS Service',
                'content': '''
                <h3>AWS Route 53: Managed DNS Service</h3>
                <p>Highly available and scalable Domain Name System (DNS) web service.</p>
                
                <h4>Route 53 Features:</h4>
                <ul>
                    <li><strong>Domain Registration</strong>: Register and manage domains</li>
                    <li><strong>DNS Routing</strong>: Route traffic to AWS and external resources</li>
                    <li><strong>Health Checking</strong>: Monitor endpoint health</li>
                    <li><strong>Traffic Flow</strong>: Visual traffic management</li>
                </ul>
                
                <h4>Routing Policies:</h4>
                <ol>
                    <li><strong>Simple</strong>: Basic DNS record (no health checks)</li>
                    <li><strong>Weighted</strong>: Split traffic based on weights</li>
                    <li><strong>Latency-based</strong>: Route to region with lowest latency</li>
                    <li><strong>Failover</strong>: Active-passive failover configuration</li>
                    <li><strong>Geolocation</strong>: Route based on user location</li>
                    <li><strong>Multivalue Answer</strong>: Return multiple healthy records</li>
                </ol>
                
                <h4>Record Types:</h4>
                <ul>
                    <li><strong>A/AAAA</strong>: IPv4/IPv6 address</li>
                    <li><strong>CNAME</strong>: Canonical name (alias)</li>
                    <li><strong>MX</strong>: Mail exchange</li>
                    <li><strong>TXT</strong>: Text records (verification, SPF)</li>
                    <li><strong>ALIAS</strong>: AWS-specific record (maps to AWS resource)</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create Route 53 Record</h5>
                    <pre><code class="language-bash">
# Create hosted zone
aws route53 create-hosted-zone \\
    --name example.com \\
    --caller-reference $(date +%s)

# Create A record pointing to EC2 instance
aws route53 change-resource-record-sets \\
    --hosted-zone-id Z123456789ABC \\
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.example.com",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{ "Value": "54.123.456.789" }]
            }
        }]
    }'
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Route 53 - Smart DNS Management

### 📖 **What You'll Learn:**
- DNS fundamentals and record types
- Route 53 routing policies
- Health checks and failover
- Domain registration and management

### 🔑 **Routing Policies:**
1. **Simple**: Basic A/CNAME records
2. **Weighted**: Split traffic (A/B testing)
3. **Latency-based**: Lowest latency region
4. **Failover**: Active-passive setup
5. **Geolocation**: Location-based routing
6. **Multivalue**: Multiple healthy IPs

### 🏗️ **Route 53 Architecture:**
User Request → Route 53 → Routing Policy → Healthy Endpoint
↓ ↓ ↓ ↓
DNS Query Hosted Zone Health Check EC2/ELB/S3

text

### ⚠️ **DNS Management Mistakes:**
- Long TTLs during changes ❌
- No health checks for critical services ❌
- Using CNAME for zone apex ❌
- Not monitoring DNS resolution ❌

### ✅ **Route 53 Best Practices:**
1. ✅ **Use ALIAS records for AWS resources**
2. ✅ **Implement health checks for critical endpoints**
3. ✅ **Use failover routing for high availability**
4. ✅ **Monitor Route 53 metrics in CloudWatch**
5. ✅ **Use Traffic Flow for complex routing**
6. ✅ **Enable DNSSEC for security**

### 🌍 **Global Application Setup:**
example.com
├── us.example.com (Weighted: 60%) → us-east-1
├── eu.example.com (Weighted: 30%) → eu-west-1
└── ap.example.com (Weighted: 10%) → ap-southeast-2
↓
Latency-based Routing → Closest Region

text

### 🔧 **Creating a Health Check:**
```bash
# Create health check
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTP",
        "ResourcePath": "/health",
        "Port": 80,
        "IPAddress": "203.0.113.10",
        "RequestInterval": 30,
        "FailureThreshold": 3
    }'
```'''
            }
        ]
    },
    {
        'title': 'AWS Serverless Applications',
        'slug': 'aws-serverless',
        'description': 'Build scalable applications using Lambda, API Gateway, DynamoDB, and Step Functions.',
        'difficulty': 'intermediate',
        'duration': 18,
        'modules': [
            {
                'title': 'AWS Lambda Fundamentals',
                'content': '''
                <h3>AWS Lambda: Serverless Compute</h3>
                <p>Run code without provisioning or managing servers. Pay only for compute time consumed.</p>
                
                <h4>Lambda Key Concepts:</h4>
                <ul>
                    <li><strong>Function</strong>: Your code packaged as a Lambda function</li>
                    <li><strong>Trigger</strong>: Event source that invokes function (API Gateway, S3, etc.)</li>
                    <li><strong>Runtime</strong>: Execution environment (Python, Node.js, Java, etc.)</li>
                    <li><strong>Layer</strong>: Share code/libraries across functions</li>
                    <li><strong>Concurrency</strong>: Number of function instances executing simultaneously</li>
                </ul>
                
                <h4>Lambda Limits (Important):</h4>
                <table class="table table-bordered">
                    <thead>
                        <tr><th>Resource</th><th>Limit</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Memory</td><td>128 MB - 10,240 MB (in 1 MB increments)</td></tr>
                        <tr><td>Timeout</td><td>Up to 15 minutes</td></tr>
                        <tr><td>Package Size</td><td>50 MB (zipped), 250 MB (unzipped)</td></tr>
                        <tr><td>Environment Variables</td><td>4 KB total</td></tr>
                        <tr><td>Concurrent Executions</td><td>1,000 default (can be increased)</td></tr>
                    </tbody>
                </table>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create Lambda Function (Python)</h5>
                    <pre><code class="language-python">
import json

def lambda_handler(event, context):
    """
    Basic Lambda function that returns a greeting.
    """
    # Parse query string parameters
    name = event.get('queryStringParameters', {}).get('name', 'World')
    
    # Construct response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': f'Hello {name}!',
            'timestamp': context.aws_request_id
        })
    }
    
    return response
                    </code></pre>
                </div>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Deploy Lambda via CLI</h5>
                    <pre><code class="language-bash">
# Create deployment package
zip function.zip lambda_function.py

# Create Lambda function
aws lambda create-function \\
    --function-name hello-world \\
    --runtime python3.9 \\
    --role arn:aws:iam::123456789012:role/lambda-execution-role \\
    --handler lambda_function.lambda_handler \\
    --zip-file fileb://function.zip \\
    --memory-size 128 \\
    --timeout 30

# Invoke Lambda function
aws lambda invoke \\
    --function-name hello-world \\
    --payload '{"queryStringParameters": {"name": "AWS Learner"}}' \\
    response.json

cat response.json
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 AWS Lambda - Serverless Compute

### 📖 **What You'll Learn:**
- Lambda function creation and deployment
- Event sources and triggers
- Memory and timeout configuration
- Best practices for serverless functions

### 🔑 **Lambda Key Concepts:**
1. **Function**: Your code (Python, Node.js, Java, etc.)
2. **Trigger**: What invokes your function (API, S3, SQS)
3. **Runtime**: Execution environment
4. **Concurrency**: Parallel executions
5. **Cold Start**: Initial execution delay

### 🏗️ **Lambda Execution Flow:**
Event → Lambda Service → Function Execution → Response
↓ ↓ ↓ ↓
API Call Runtime Your Code JSON/Result
S3 Event Memory Environment Error
SQS Msg Timeout Layers

text

### ⚠️ **Common Lambda Mistakes:**
- Functions doing too much (not single-purpose) ❌
- Not handling errors properly ❌
- Ignoring cold start performance ❌
- No monitoring or logging ❌

### ✅ **Lambda Best Practices:**
1. ✅ **Keep functions small and focused**
2. ✅ **Use environment variables for configuration**
3. ✅ **Implement proper error handling**
4. ✅ **Use Lambda layers for shared code**
5. ✅ **Set appropriate memory and timeout**
6. ✅ **Enable X-Ray tracing for debugging**
7. ✅ **Use provisioned concurrency for critical functions**

### 💰 **Cost Optimization:**
- Right-size memory (more memory = more CPU = faster)
- Use shorter timeouts
- Implement async processing for non-critical tasks
- Use SQS for batch processing
- Monitor with Cost Explorer

### 🔧 **Python Lambda Template:**
```python
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Process event
        result = process_data(event)
        
        # Log execution
        print(f"Execution ID: {context.aws_request_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        # Error handling
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```'''
            },
            {
                'title': 'API Gateway Integration',
                'content': '''
                <h3>API Gateway: Managed API Service</h3>
                <p>Create, publish, maintain, monitor, and secure RESTful and WebSocket APIs.</p>
                
                <h4>API Gateway Features:</h4>
                <ul>
                    <li><strong>REST APIs</strong>: RESTful API endpoints (HTTP methods)</li>
                    <li><strong>HTTP APIs</strong>: Lower cost, faster performance</li>
                    <li><strong>WebSocket APIs</strong>: Real-time two-way communication</li>
                    <li><strong>Stages</strong>: Deployments (dev, test, prod)</li>
                    <li><strong>Usage Plans</strong>: API key management and throttling</li>
                </ul>
                
                <h4>Integration Types:</h4>
                <ol>
                    <li><strong>Lambda Integration</strong>: Most common - invoke Lambda function</li>
                    <li><strong>HTTP Integration</strong>: Proxy to HTTP backend</li>
                    <li><strong>AWS Service Integration</strong>: Direct to AWS services</li>
                    <li><strong>Mock Integration</strong>: Return mock response (testing)</li>
                    <li><strong>VPC Link</strong>: Connect to private resources in VPC</li>
                </ol>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create REST API via CLI</h5>
                    <pre><code class="language-bash">
# Create REST API
aws apigateway create-rest-api \\
    --name "HelloWorldAPI" \\
    --description "API for Hello World Lambda"

# Get API ID
API_ID=$(aws apigateway get-rest-apis \\
    --query "items[?name=='HelloWorldAPI'].id" \\
    --output text)

# Create deployment
aws apigateway create-deployment \\
    --rest-api-id $API_ID \\
    --stage-name "prod"

echo "API URL: https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod"
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 API Gateway - Serverless APIs

### 📖 **What You'll Learn:**
- REST vs HTTP vs WebSocket APIs
- Integration types (Lambda, HTTP, AWS services)
- Stages and deployments
- Authentication and authorization

### 🔑 **API Types:**
1. **REST APIs**: Full-featured (request/response)
2. **HTTP APIs**: Faster, cheaper (JWT auth only)
3. **WebSocket APIs**: Real-time bidirectional
4. **REST APIs Private**: VPC-only access

### 🏗️ **API Gateway Architecture:**
Client → API Gateway → Integration → Backend
↓ ↓ ↓ ↓
Request Auth/Throttle Lambda Response
Rate Limit HTTP
Caching AWS Service

text

### ⚠️ **API Gateway Mistakes:**
- Not using stages for environments ❌
- No authentication on public APIs ❌
- Not implementing rate limiting ❌
- Forgetting to deploy changes ❌

### ✅ **API Gateway Best Practices:**
1. ✅ **Use HTTP APIs when possible (cheaper)**
2. ✅ **Implement authentication (Cognito, IAM, API keys)**
3. ✅ **Enable caching for static responses**
4. ✅ **Use usage plans for API keys**
5. ✅ **Implement throttling to prevent abuse**
6. ✅ **Enable CloudWatch logging and metrics**
7. ✅ **Use custom domains for production**

### 🔐 **Security Options:**
- **IAM**: AWS users/roles
- **Cognito**: User pools
- **Lambda Authorizer**: Custom logic
- **API Keys**: Simple authentication

### 🌐 **CORS Configuration:**
```yaml
cors:
  allow_origins:
    - "https://example.com"
  allow_methods:
    - GET
    - POST
    - PUT
    - DELETE
  allow_headers:
    - Content-Type
    - Authorization
  max_age: 3600
```'''
            },
            {
                'title': 'DynamoDB NoSQL Database',
                'content': '''
                <h3>DynamoDB: Managed NoSQL Database</h3>
                <p>Fast and flexible NoSQL database service for any scale.</p>
                
                <h4>DynamoDB Components:</h4>
                <ul>
                    <li><strong>Tables</strong>: Collection of items</li>
                    <li><strong>Items</strong>: Individual records (similar to rows)</li>
                    <li><strong>Attributes</strong>: Data elements in items (similar to columns)</li>
                    <li><strong>Primary Key</strong>: Uniquely identifies each item
                        <ul>
                            <li><strong>Partition Key</strong>: Single attribute (HASH)</li>
                            <li><strong>Composite Key</strong>: Partition + Sort key (HASH+RANGE)</li>
                        </ul>
                    </li>
                </ul>
                
                <h4>Capacity Modes:</h4>
                <ul>
                    <li><strong>Provisioned</strong>: Specify RCU/WCU (predictable workload)</li>
                    <li><strong>On-Demand</strong>: Pay per request (unpredictable workload)</li>
                    <li><strong>Auto Scaling</strong>: Automatically adjust capacity</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create DynamoDB Table</h5>
                    <pre><code class="language-bash">
# Create table with partition key
aws dynamodb create-table \\
    --table-name Users \\
    --attribute-definitions AttributeName=UserId,AttributeType=S \\
    --key-schema AttributeName=UserId,KeyType=HASH \\
    --billing-mode PAY_PER_REQUEST

# Create table with composite key
aws dynamodb create-table \\
    --table-name Orders \\
    --attribute-definitions \\
        AttributeName=CustomerId,AttributeType=S \\
        AttributeName=OrderDate,AttributeType=S \\
    --key-schema \\
        AttributeName=CustomerId,KeyType=HASH \\
        AttributeName=OrderDate,KeyType=RANGE \\
    --billing-mode PROVISIONED \\
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
                    </code></pre>
                </div>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Basic DynamoDB Operations</h5>
                    <pre><code class="language-bash">
# Put item
aws dynamodb put-item \\
    --table-name Users \\
    --item '{
        "UserId": {"S": "user123"},
        "Name": {"S": "John Doe"},
        "Email": {"S": "john@example.com"},
        "Age": {"N": "30"}
    }'

# Get item
aws dynamodb get-item \\
    --table-name Users \\
    --key '{"UserId": {"S": "user123"}}'

# Query items
aws dynamodb query \\
    --table-name Orders \\
    --key-condition-expression "CustomerId = :cid" \\
    --expression-attribute-values '{":cid":{"S":"cust456"}}'
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 DynamoDB - NoSQL at Scale

### 📖 **What You'll Learn:**
- DynamoDB table design
- Primary keys (partition and sort keys)
- Capacity modes (provisioned vs on-demand)
- Query and scan operations

### 🔑 **DynamoDB Components:**
1. **Table**: Collection of items
2. **Item**: Individual record
3. **Attribute**: Data element
4. **Primary Key**: Partition (HASH) + optional Sort (RANGE)
5. **Secondary Indexes**: GSI (global) and LSI (local)

### 🏗️ **DynamoDB Architecture:**
Table → Partitions → Items → Attributes
↓ ↓ ↓ ↓
Name Hash Key Record Key-Value
Sort Key Data Types

text

### ⚠️ **DynamoDB Mistakes:**
- Using scans instead of queries ❌
- Not designing for access patterns ❌
- Wrong primary key design ❌
- No backup strategy ❌

### ✅ **DynamoDB Best Practices:**
1. ✅ **Design tables around access patterns**
2. ✅ **Use composite keys for efficient queries**
3. ✅ **Implement Global Secondary Indexes (GSI)**
4. ✅ **Use DynamoDB Streams for real-time processing**
5. ✅ **Enable Point-in-Time Recovery (PITR)**
6. ✅ **Use DAX for read-heavy workloads**
7. ✅ **Monitor with CloudWatch metrics**

### 🗝️ **Key Design Patterns:**
- **Single Table Design**: All entities in one table
- **Composite Keys**: Enable efficient queries
- **GSI**: Query by alternate keys
- **LSI**: Query within same partition key

### 💰 **Capacity Planning:**
- **On-Demand**: Unpredictable workloads
- **Provisioned**: Predictable workloads
- **Auto Scaling**: Automatic capacity adjustment
- **Reserved Capacity**: Cost savings for steady state

### 📊 **Example Table Design:**
Orders Table
├── PK: CUST#<customer_id> (Partition Key)
├── SK: ORDER#<order_id>#<date> (Sort Key)
├── Attributes: amount, status, items
└── GSI: GSI1-PK: STATUS#<status>, GSI1-SK: <date>

'''
            },
            {
                'title': 'Step Functions Workflows',
                'content': '''
                <h3>AWS Step Functions: Serverless Workflows</h3>
                <p>Coordinate multiple AWS services into serverless workflows.</p>
                
                <h4>Step Functions Concepts:</h4>
                <ul>
                    <li><strong>State Machine</strong>: Workflow definition</li>
                    <li><strong>States</strong>: Individual steps in workflow</li>
                    <li><strong>Tasks</strong>: Perform work (invoke Lambda, etc.)</li>
                    <li><strong>Choice</strong>: Add branching logic</li>
                    <li><strong>Parallel</strong>: Run steps in parallel</li>
                    <li><strong>Map</strong>: Process arrays of data</li>
                </ul>
                
                <h4>Workflow Types:</h4>
                <ul>
                    <li><strong>Standard</strong>: Long-running workflows (up to 1 year)</li>
                    <li><strong>Express</strong>: Short-running workflows (up to 5 minutes)</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Simple State Machine Definition (ASL)</h5>
                    <pre><code class="language-json">
{
  "Comment": "Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:validate-order",
      "Next": "ProcessPayment"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process-payment",
      "Next": "CheckInventory"
    },
    "CheckInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:check-inventory",
      "Next": "ShipOrder"
    },
    "ShipOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ship-order",
      "End": true
    }
  }
}
                    </code></pre>
                </div>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create Step Function</h5>
                    <pre><code class="language-bash">
# Create state machine
aws stepfunctions create-state-machine \\
    --name "OrderProcessing" \\
    --definition file://workflow-definition.json \\
    --role-arn arn:aws:iam::123456789012:role/StepFunctionsExecutionRole

# Start execution
aws stepfunctions start-execution \\
    --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:OrderProcessing \\
    --input '{"orderId": "12345", "customerId": "cust789"}'
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Step Functions - Serverless Workflows

### 📖 **What You'll Learn:**
- State machine concepts
- Workflow types (Standard vs Express)
- State types (Task, Choice, Parallel, Map)
- Error handling and retries

### 🔑 **Step Functions States:**
1. **Task**: Perform work (Lambda, ECS, etc.)
2. **Choice**: Branching logic (if/else)
3. **Parallel**: Run steps concurrently
4. **Map**: Process arrays in parallel
5. **Wait**: Delay execution
6. **Pass**: Pass input to output
7. **Succeed/Fail**: End states

### 🏗️ **Workflow Types:**
- **Standard**: Long-running (1 year max), exactly-once
- **Express**: Short-running (5 min max), at-least-once
- **Standard**: $0.025 per state transition
- **Express**: $0.000001 per request + $0.00001667 per GB-second

### ⚠️ **Workflow Mistakes:**
- No error handling in workflows ❌
- Not using retry policies ❌
- Complex nested choices ❌
- No monitoring or alerts ❌

### ✅ **Step Functions Best Practices:**
1. ✅ **Use Standard workflows for business processes**
2. ✅ **Use Express workflows for high-volume, short tasks**
3. ✅ **Implement comprehensive error handling**
4. ✅ **Use retry policies with exponential backoff**
5. ✅ **Monitor with CloudWatch metrics and logs**
6. ✅ **Use input/output processing for data transformation**
7. ✅ **Implement idempotency for Express workflows**

### 🔄 **Error Handling Pattern:**
```json
"Retry": [{
  "ErrorEquals": ["States.ALL"],
  "IntervalSeconds": 1,
  "MaxAttempts": 3,
  "BackoffRate": 2
}],
"Catch": [{
  "ErrorEquals": ["States.ALL"],
  "Next": "ErrorHandler",
  "ResultPath": "$.error"
}]
🚀 Common Use Cases:
Order Processing: Validate → Process → Ship

ETL Pipelines: Extract → Transform → Load

Approval Workflows: Submit → Approve/Reject → Notify

Batch Processing: Split → Process → Merge

📈 Monitoring:
CloudWatch metrics for success/failure rates

X-Ray tracing for performance insights

CloudTrail logs for audit trails

Custom dashboards for business metrics'''
},
{
'title': 'Serverless Best Practices',
'content': '''
<h3>Serverless Architecture Best Practices</h3>

text
          <h4>Design Principles:</h4>
          <ol>
              <li><strong>Use Single Purpose Functions</strong>: Each Lambda should do one thing well</li>
              <li><strong>Keep Functions Stateless</strong>: Store state in external services (DynamoDB, S3)</li>
              <li><strong>Optimize Cold Starts</strong>: Keep deployment packages small, use provisioned concurrency</li>
              <li><strong>Implement Proper Error Handling</strong>: Use dead letter queues (DLQ) for failed invocations</li>
              <li><strong>Monitor Everything</strong>: Use CloudWatch Logs, Metrics, and X-Ray tracing</li>
          </ol>
          
          <h4>Performance Optimization:</h4>
          <ul>
              <li><strong>Memory Allocation</strong>: More memory = more CPU = faster execution (cost trade-off)</li>
              <li><strong>Environment Variables</strong>: Use for configuration, not secrets (use Secrets Manager)</li>
              <li><strong>Lambda Layers</strong>: Share common libraries across functions</li>
              <li><strong>Concurrency Control</strong>: Set reserved concurrency for critical functions</li>
          </ul>
          
          <h4>Cost Optimization:</h4>
          <ul>
              <li>Use HTTP APIs instead of REST APIs when possible</li>
              <li>Choose DynamoDB on-demand for unpredictable workloads</li>
              <li>Implement proper cleanup (delete unused functions, APIs)</li>
              <li>Use CloudWatch alarms for cost monitoring</li>
          </ul>
          
          <div class="tips mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
              <h5><i class="fas fa-lightbulb"></i> Pro Tip: Serverless Testing Strategy</h5>
              <ul>
                  <li><strong>Unit Tests</strong>: Test Lambda functions locally with mocked services</li>
                  <li><strong>Integration Tests</strong>: Test with real AWS services in dev account</li>
                  <li><strong>Load Tests</strong>: Simulate production traffic patterns</li>
                  <li><strong>Chaos Testing</strong>: Test failure scenarios (service outages, throttling)</li>
              </ul>
          </div>
          ''',
          'mini_tutorial': '''## 🎯 Serverless Best Practices
📖 What You'll Learn:
Serverless design principles

Performance optimization techniques

Cost management strategies

Monitoring and observability

🔑 Design Principles:
Single Responsibility: One function = one job

Stateless: Externalize state (DynamoDB, S3)

Event-Driven: React to events, don't poll

Loose Coupling: Services communicate via events

Design for Failure: Implement retries and fallbacks

🏗️ Serverless Architecture:
text
Events → API Gateway → Lambda → DynamoDB
   ↓         ↓          ↓         ↓
S3/SQS   Auth/Rate    Business   Data
SNS/Kinesis  Limiting  Logic    Storage
⚠️ Serverless Anti-Patterns:
Lambda functions as cron jobs ❌

Functions calling functions synchronously ❌

No monitoring or alerting ❌

Hardcoded configuration ❌

✅ Performance Optimization:
✅ Right-size Lambda memory (more memory = more CPU)

✅ Use provisioned concurrency for critical functions

✅ Minimize deployment package size

✅ Use Lambda layers for common dependencies

✅ Implement connection pooling for databases

✅ Use async processing when possible

💰 Cost Optimization:
Lambda: Right-size memory, shorter timeouts

API Gateway: Use HTTP APIs instead of REST

DynamoDB: Choose on-demand for unpredictable workloads

Step Functions: Use Express for high-volume, short workflows

Monitoring: Set budget alerts, clean up unused resources

🛡️ Security Best Practices:
Use IAM roles with least privilege

Store secrets in Secrets Manager or Parameter Store

Encrypt data at rest and in transit

Implement VPC endpoints for private access

Regular security scanning and compliance checks

📊 Monitoring Strategy:
CloudWatch: Metrics, logs, alarms

X-Ray: Distributed tracing, performance insights

CloudTrail: Audit trails, compliance

Custom Metrics: Business KPIs

Dashboards: Real-time visibility

🧪 Testing Strategy:
Unit Tests: Local testing with mocks

Integration Tests: Real AWS services

Load Tests: Simulate production traffic

Chaos Tests: Failure scenario testing

Canary Deployments: Gradual rollout'''
}
]
},
{
'title': 'AWS Security & Compliance',
'slug': 'aws-security',
'description': 'Learn AWS security best practices, encryption, monitoring, and compliance frameworks.',
'difficulty': 'advanced',
'duration': 20,
'modules': [
{
'title': 'IAM Advanced Features',
'content': '''
<h3>Advanced IAM Concepts</h3>

text
          <h4>IAM Policy Evaluation Logic:</h4>
          <ol>
              <li>By default, all requests are <strong>DENIED</strong></li>
              <li>Explicit ALLOW overrides default DENY</li>
              <li>Explicit DENY overrides any ALLOW</li>
              <li>Organization SCPs can DENY even if IAM allows</li>
          </ol>
          
          <h4>Advanced IAM Features:</h4>
          <ul>
              <li><strong>Permissions Boundaries</strong>: Maximum permissions a user/role can have</li>
              <li><strong>Service Control Policies (SCPs)</strong>: Organization-wide permission boundaries</li>
              <li><strong>IAM Conditions</strong>: Fine-grained access control based on context</li>
              <li><strong>Resource-based Policies</strong>: Attach policies directly to resources (S3, Lambda)</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> IAM Policy with Conditions</h5>
              <pre><code class="language-json">
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": "s3:",
"Resource": "",
"Condition": {
"IpAddress": {
"aws:SourceIp": "203.0.113.0/24"
},
"Bool": {
"aws:SecureTransport": "true"
},
"NumericLessThanEquals": {
"s3:max-keys": "10"
}
}
}
]
}
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 Advanced IAM - Fine-Grained Control

📖 What You'll Learn:
IAM policy evaluation logic

Permissions boundaries and SCPs

IAM conditions and context-based access

Resource-based policies

🔑 IAM Policy Evaluation:
Default: All requests DENIED

Explicit ALLOW: Overrides default DENY

Explicit DENY: Overrides any ALLOW

SCP DENY: Overrides IAM ALLOW (organization level)

🏗️ Advanced IAM Architecture:
text
Organization SCPs (Allow/Deny)
        ↓
IAM Permissions Boundaries (Max permissions)
        ↓
IAM Policies (Allow/Deny)
        ↓
Resource-based Policies (S3, Lambda)
        ↓
    Request
⚠️ Advanced IAM Mistakes:
Not using permission boundaries for power users ❌

Overly permissive SCPs ❌

Ignoring resource-based policies ❌

Not auditing IAM policies regularly ❌

✅ Advanced IAM Best Practices:
✅ Use permissions boundaries for admin users

✅ Implement SCPs for organization-wide guardrails

✅ Use IAM conditions for fine-grained access

✅ Regularly audit IAM policies with Access Analyzer

✅ Use IAM Roles Anywhere for on-premises workloads

✅ Implement IAM Identity Center for multi-account access

🔐 Condition Examples:
json
"Condition": {
  "IpAddress": {"aws:SourceIp": "203.0.113.0/24"},
  "Bool": {"aws:SecureTransport": "true"},
  "NumericLessThan": {"s3:max-keys": "100"},
  "DateGreaterThan": {"aws:CurrentTime": "2024-01-01T00:00:00Z"},
  "StringEquals": {"aws:PrincipalTag/Department": "Engineering"}
}
🏢 Organization SCP Example:
json
{
  "Effect": "Deny",
  "Action": [
    "iam:CreateUser",
    "iam:DeleteUser",
    "iam:CreateAccessKey"
  ],
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:PrincipalOrgPaths": "o-abc123/r-def456/ou-ghi789/*"
    }
  }
}
```'''
            },
            {
                'title': 'KMS - Key Management Service',
                'content': '''
                <h3>AWS KMS: Managed Encryption Keys</h3>
                <p>Create and control encryption keys used to encrypt your data.</p>
                
                <h4>Key Types:</h4>
                <ul>
                    <li><strong>AWS Managed Keys</strong>: Created automatically by AWS services (free)</li>
                    <li><strong>Customer Managed Keys (CMK)</strong>: Created and managed by you
                        <ul>
                            <li><strong>Symmetric</strong>: Same key for encryption/decryption (AES-256)</li>
                            <li><strong>Asymmetric</strong>: Public/private key pair (RSA, ECC)</li>
                        </ul>
                    </li>
                </ul>
                
                <h4>Key Policies:</h4>
                <p>Resource-based policies that define who can use/manage the key. Default key policy allows root user full access.</p>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create CMK and Encrypt Data</h5>
                    <pre><code class="language-bash">
# Create customer managed key
aws kms create-key \\
    --description "Production Database Key" \\
    --key-usage ENCRYPT_DECRYPT \\
    --origin AWS_KMS

# Encrypt data
aws kms encrypt \\
    --key-id alias/MyKey \\
    --plaintext fileb://secret.txt \\
    --output text \\
    --query CiphertextBlob \\
    > encrypted.txt

# Decrypt data
aws kms decrypt \\
    --ciphertext-blob fileb://encrypted.txt \\
    --output text \\
    --query Plaintext \\
    > decrypted.txt
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 KMS - Encryption Management

### 📖 **What You'll Learn:**
- AWS KMS key types and management
- Encryption/decryption operations
- Key policies and permissions
- Integration with AWS services

### 🔑 **KMS Key Types:**
1. **AWS Managed Keys**: Automatic, free (aws/s3, aws/ebs, etc.)
2. **Customer Managed Keys (CMK)**: You control
   - **Symmetric**: AES-256 (encrypt/decrypt)
   - **Asymmetric**: RSA/ECC (sign/verify, encrypt/decrypt)
3. **Custom Key Store**: HSMs you manage

### 🏗️ **KMS Architecture:**
Your Data → KMS Key → Encryption → Encrypted Data
↓ ↓ ↓ ↓
S3/EBS/RDS CMK/AWS AES-256 Stored in
Managed RSA/ECC Service

text

### ⚠️ **KMS Mistakes:**
- Not rotating keys regularly ❌
- Granting too many users key access ❌
- Not backing up key material ❌
- Using default key policy ❌

### ✅ **KMS Best Practices:**
1. ✅ **Use CMKs for production workloads**
2. ✅ **Implement automatic key rotation (yearly)**
3. ✅ **Use key aliases (not key IDs) in code**
4. ✅ **Enable CloudTrail for KMS API logging**
5. ✅ **Use grants for temporary access**
6. ✅ **Implement key policies with least privilege**
7. ✅ **Use envelope encryption for large data**

### 🔐 **Key Policy Example:**
```json
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::123456789012:role/EncryptionRole"
  },
  "Action": [
    "kms:Encrypt",
    "kms:Decrypt",
    "kms:GenerateDataKey"
  ],
  "Resource": "*"
}
🔄 Key Rotation Strategy:
Automatic: Yearly rotation (new backing key)

Manual: Create new key, update applications

Aliases: Never change in code

Data Re-encryption: Required for some services

🛡️ Security Considerations:
Enable key deletion protection

Use multi-region keys for DR

Monitor key usage with CloudTrail

Implement separation of duties (admin vs user)

Use conditions in key policies

🔧 Envelope Encryption:
python
import boto3
from cryptography.fernet import Fernet

# Generate data key
kms = boto3.client('kms')
response = kms.generate_data_key(KeyId='alias/MyKey', KeySpec='AES_256')

# Use data key for encryption
cipher = Fernet(response['Plaintext'])
encrypted_data = cipher.encrypt(b"Secret data")

# Store encrypted data key with data
result = {
    'encrypted_data': encrypted_data,
    'encrypted_key': response['CiphertextBlob']
}
```'''
            },
            {
                'title': 'CloudTrail and CloudWatch',
                'content': '''
                <h3>AWS Monitoring and Auditing</h3>
                
                <h4>AWS CloudTrail:</h4>
                <p>Logs API calls and account activity for security analysis and compliance.</p>
                <ul>
                    <li><strong>Management Events</strong>: Operations on AWS resources (default, free)</li>
                    <li><strong>Data Events</strong>: Resource operations (S3 object-level, Lambda invoke)</li>
                    <li><strong>Insights Events</strong>: Automated analysis of normal activity patterns</li>
                </ul>
                
                <h4>Amazon CloudWatch:</h4>
                <p>Monitoring and observability service for AWS resources and applications.</p>
                <ul>
                    <li><strong>Metrics</strong>: Time-ordered data points (CPU utilization, request count)</li>
                    <li><strong>Logs</strong>: Log data from AWS services and applications</li>
                    <li><strong>Alarms</strong>: Monitor metrics and trigger actions</li>
                    <li><strong>Dashboards</strong>: Customizable monitoring views</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Create CloudTrail Trail</h5>
                    <pre><code class="language-bash">
# Create trail for all regions
aws cloudtrail create-trail \\
    --name SecurityAuditTrail \\
    --s3-bucket-name my-cloudtrail-logs-2024 \\
    --is-multi-region-trail \\
    --enable-log-file-validation

# Start logging
aws cloudtrail start-logging --name SecurityAuditTrail

# Create CloudWatch alarm for failed logins
aws cloudwatch put-metric-alarm \\
    --alarm-name "HighFailedLogins" \\
    --metric-name FailedLoginEvents \\
    --namespace AWS/CloudTrail \\
    --statistic Sum \\
    --period 300 \\
    --threshold 10 \\
    --comparison-operator GreaterThanThreshold \\
    --evaluation-periods 1 \\
    --alarm-actions arn:aws:sns:us-east-1:123456789012:SecurityAlerts
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Monitoring & Auditing: CloudTrail + CloudWatch

### 📖 **What You'll Learn:**
- CloudTrail for API auditing
- CloudWatch for monitoring
- Security event detection
- Compliance reporting

### 🔑 **CloudTrail Event Types:**
1. **Management Events**: Control plane operations (free)
2. **Data Events**: Data plane operations (S3, Lambda - extra cost)
3. **Insights Events**: Anomaly detection (extra cost)

### 🔑 **CloudWatch Components:**
1. **Metrics**: Numerical data (CPU, requests, errors)
2. **Logs**: Text data (application logs, VPC flow logs)
3. **Alarms**: Automated responses to metrics
4. **Dashboards**: Custom visualization

### 🏗️ **Monitoring Architecture:**
AWS Services → CloudTrail → S3/CloudWatch Logs
↓ ↓ ↓
Metrics API Auditing Log Analysis
↓ ↓ ↓
CloudWatch → Alarms → SNS/SSM/Lambda

text

### ⚠️ **Monitoring Mistakes:**
- Not enabling CloudTrail in all regions ❌
- No log file validation ❌
- Missing critical alarms ❌
- Not retaining logs for compliance ❌

### ✅ **Monitoring Best Practices:**
1. ✅ **Enable CloudTrail in all regions**
2. ✅ **Enable log file validation (integrity)**
3. ✅ **Send CloudTrail logs to CloudWatch Logs**
4. ✅ **Create organization trail for multi-account**
5. ✅ **Implement CloudWatch alarms for security events**
6. ✅ **Use CloudWatch dashboards for visibility**
7. ✅ **Retain logs for compliance requirements (1-7 years)**

### 🔔 **Critical Security Alarms:**
- Root user login
- IAM policy changes
- Security group changes
- Network ACL changes
- Failed authentication attempts
- Unauthorized API calls
- S3 bucket policy changes

### 📊 **CloudWatch Alarm Example:**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "RootUserLogin" \
    --metric-name "RootUserEventCount" \
    --namespace AWS/CloudTrail \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:SecurityTeam \
    --dimensions Name=EventName,Value=ConsoleLogin
🛡️ Compliance Requirements:
PCI DSS: 1 year log retention

HIPAA: 6 year log retention

SOC 2: Evidence collection

GDPR: Audit trails for data access'''
},
{
'title': 'WAF and Shield',
'content': '''
<h3>AWS Web Application Firewall (WAF) and Shield</h3>

text
          <h4>AWS WAF:</h4>
          <p>Protects web applications from common web exploits.</p>
          <ul>
              <li><strong>Web ACLs</strong>: Collection of rules for protecting resources</li>
              <li><strong>Rules</strong>: Conditions for inspecting web requests</li>
              <li><strong>Rule Groups</strong>: Reusable set of rules (managed or custom)</li>
              <li><strong>Integrations</strong>: CloudFront, ALB, API Gateway</li>
          </ul>
          
          <h4>AWS Shield:</h4>
          <p>Managed DDoS protection service.</p>
          <ul>
              <li><strong>Shield Standard</strong>: Automatic, no cost protection</li>
              <li><strong>Shield Advanced</strong>: Enhanced DDoS protection with 24/7 support</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create WAF Web ACL</h5>
              <pre><code class="language-bash">
Create IP set for blocked IPs
aws wafv2 create-ip-set \
--name BlockedIPs \
--scope REGIONAL \
--ip-address-version IPV4 \
--addresses "203.0.113.0/24" "198.51.100.0/24"

Create web ACL
aws wafv2 create-web-acl \
--name ProductionWebACL \
--scope REGIONAL \
--default-action Allow={} \
--visibility-config \
SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=ProductionWebACLMetrics \
--rules '[
{
"Name": "AWSManagedRulesCommonRuleSet",
"Priority": 1,
"Statement": {
"ManagedRuleGroupStatement": {
"VendorName": "AWS",
"Name": "AWSManagedRulesCommonRuleSet"
}
},
"OverrideAction": { "None": {} },
"VisibilityConfig": {
"SampledRequestsEnabled": true,
"CloudWatchMetricsEnabled": true,
"MetricName": "AWSManagedRulesCommonRuleSet"
}
}
]'
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 WAF & Shield - Application Protection

📖 What You'll Learn:
AWS WAF for web application protection

AWS Shield for DDoS protection

Rule creation and management

Monitoring and response

🔑 AWS WAF Components:
Web ACL: Rule collection applied to resources

Rules: Conditions to match requests

Rule Groups: Reusable rule sets (managed/custom)

IP Sets: Collections of IP addresses

🔑 AWS Shield Tiers:
Standard: Automatic, free (ALB, CloudFront, Route 53)

Advanced: Enhanced protection ($3,000/month + usage)

24/7 DDoS response team

Cost protection for scaling

Advanced reporting

🏗️ Protection Architecture:
text
Internet → CloudFront/ALB → AWS WAF → Your Application
    ↓           ↓             ↓            ↓
  Traffic   Distribution   Rule Evaluation  Backend
              Shield Std.     Block/Allow   Servers
⚠️ Protection Mistakes:
No WAF on public-facing applications ❌

Not using managed rule groups ❌

No monitoring of WAF/Shield events ❌

Not testing WAF rules ❌

✅ WAF & Shield Best Practices:
✅ Enable WAF on all public-facing resources

✅ Start with AWS Managed Rules

✅ Implement custom rules for your application

✅ Use Shield Advanced for critical applications

✅ Monitor WAF metrics in CloudWatch

✅ Regularly review and update rules

✅ Test WAF rules before production

🛡️ Essential WAF Rules:
AWSManagedRulesCommonRuleSet: OWASP Top 10

AWSManagedRulesAmazonIpReputationList: Bad bots

AWSManagedRulesAnonymousIpList: Proxies/VPNs

AWSManagedRulesKnownBadInputs: SQL injection, XSS

Rate-based rules: Prevent brute force

📈 Monitoring Strategy:
CloudWatch metrics for allowed/blocked requests

WAF logs to S3 for forensic analysis

Shield metrics for DDoS detection

Custom dashboards for visibility

Automated alerts for security events

🔧 Creating a Web ACL:
bash
# Create Web ACL with managed rules
aws wafv2 create-web-acl \
    --name Production-WebACL \
    --scope REGIONAL \
    --default-action Allow={} \
    --visibility-config \
        SampledRequestsEnabled=true,\
        CloudWatchMetricsEnabled=true,\
        MetricName=ProductionWebACL \
    --rules '[
        {
            "Name": "AWS-AWSManagedRulesCommonRuleSet",
            "Priority": 0,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet"
                }
            },
            "OverrideAction": { "None": {} },
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "AWSManagedRulesCommonRuleSet"
            }
        }
    ]'
```'''
            },
            {
                'title': 'Compliance Frameworks',
                'content': '''
                <h3>AWS Compliance and Governance</h3>
                
                <h4>Major Compliance Frameworks:</h4>
                <ul>
                    <li><strong>SOC 1/2/3</strong>: Service Organization Controls for security, availability, processing integrity</li>
                    <li><strong>PCI DSS</strong>: Payment Card Industry Data Security Standard</li>
                    <li><strong>HIPAA</strong>: Health Insurance Portability and Accountability Act</li>
                    <li><strong>GDPR</strong>: General Data Protection Regulation (EU)</li>
                    <li><strong>ISO 27001</strong>: Information security management</li>
                </ul>
                
                <h4>AWS Compliance Tools:</h4>
                <ul>
                    <li><strong>AWS Artifact</strong>: Download compliance reports</li>
                    <li><strong>AWS Config</strong>: Track resource configurations and compliance</li>
                    <li><strong>Security Hub</strong>: Centralized security and compliance view</li>
                    <li><strong>GuardDuty</strong>: Intelligent threat detection</li>
                    <li><strong>Inspector</strong>: Automated security assessments</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> AWS Config Rules</h5>
                    <pre><code class="language-bash">
# Enable AWS Config
aws configservice put-configuration-recorder \\
    --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/config-role

# Create compliance rule for encrypted S3 buckets
aws configservice put-config-rule \\
    --config-rule '{
        "ConfigRuleName": "s3-bucket-encryption-enabled",
        "Description": "Checks that S3 buckets have encryption enabled",
        "Scope": {
            "ComplianceResourceTypes": ["AWS::S3::Bucket"]
        },
        "Source": {
            "Owner": "AWS",
            "SourceIdentifier": "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
        },
        "InputParameters": "{}"
    }'
                    </code></pre>
                </div>
                
                <div class="tips mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
                    <h5><i class="fas fa-lightbulb"></i> Pro Tip: Compliance Strategy</h5>
                    <ul>
                        <li>Start with AWS Foundational Security Best Practices</li>
                        <li>Use AWS Security Hub for centralized compliance dashboard</li>
                        <li>Implement least privilege access with IAM</li>
                        <li>Enable encryption everywhere (at rest and in transit)</li>
                        <li>Regularly audit with AWS Config and CloudTrail</li>
                    </ul>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 Compliance & Governance in AWS

### 📖 **What You'll Learn:**
- Major compliance frameworks
- AWS compliance tools
- Governance strategies
- Audit and reporting

### 🔑 **Major Compliance Frameworks:**
1. **SOC 1/2/3**: Service organization controls
2. **PCI DSS**: Payment card industry
3. **HIPAA**: Healthcare data protection
4. **GDPR**: EU data privacy
5. **ISO 27001**: Information security management
6. **FedRAMP**: US government cloud

### 🔑 **AWS Compliance Tools:**
1. **AWS Artifact**: Compliance reports
2. **AWS Config**: Resource compliance tracking
3. **Security Hub**: Centralized security view
4. **GuardDuty**: Threat detection
5. **Inspector**: Vulnerability assessment

### 🏗️ **Compliance Architecture:**
AWS Services → AWS Config → Compliance Dashboard
↓ ↓ ↓
Resources Rule Evaluation Security Hub
↓ ↓ ↓
CloudTrail Compliance Status Findings

text

### ⚠️ **Compliance Mistakes:**
- Not documenting security controls ❌
- No regular compliance assessments ❌
- Ignoring AWS compliance reports ❌
- Not training staff on compliance ❌

### ✅ **Compliance Best Practices:**
1. ✅ **Start with AWS Foundational Security Best Practices**
2. ✅ **Use Security Hub for centralized compliance**
3. ✅ **Implement AWS Config for continuous compliance**
4. ✅ **Regularly review AWS Artifact reports**
5. ✅ **Enable GuardDuty for threat detection**
6. ✅ **Use AWS Organizations for multi-account governance**
7. ✅ **Implement backup and disaster recovery plans**

### 📋 **Compliance Checklist:**
- [ ] **IAM**: MFA enabled, least privilege, no root access
- [ ] **Encryption**: Data at rest and in transit
- [ ] **Logging**: CloudTrail, Config, VPC Flow Logs
- [ ] **Monitoring**: CloudWatch alarms, Security Hub
- [ ] **Backup**: Regular backups, tested restoration
- [ ] **Network**: Security groups, NACLs, WAF
- [ ] **Patch Management**: Regular updates, vulnerability scanning

### 🛡️ **Security Hub Implementation:**
```bash
# Enable Security Hub
aws securityhub enable-security-hub

# Enable security standards
aws securityhub batch-enable-standards \
    --standards-subscription-requests \
        StandardsArn="arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0"

# Get findings
aws securityhub get-findings \
    --filters '{"ComplianceStatus": [{"Value": "FAILED", "Comparison": "EQUALS"}]}'
📊 Reporting & Auditing:
Monthly compliance reports

Quarterly security assessments

Annual penetration testing

Continuous compliance monitoring

Incident response documentation

🔒 GDPR Considerations:
Data minimization

Right to erasure

Data portability

Privacy by design

Data protection officer (if required)'''
}
]
},
{
'title': 'AWS DevOps & CI/CD',
'slug': 'aws-devops',
'description': 'Implement DevOps practices with CodePipeline, CodeBuild, CodeDeploy, and Infrastructure as Code.',
'difficulty': 'intermediate',
'duration': 22,
'modules': [
{
'title': 'CI/CD Pipeline Concepts',
'content': '''
<h3>Continuous Integration and Delivery</h3>

text
          <h4>CI/CD Benefits:</h4>
          <ul>
              <li><strong>Faster Releases</strong>: Automate build, test, and deployment</li>
              <li><strong>Higher Quality</strong>: Catch issues early with automated testing</li>
              <li><strong>Reduced Risk</strong>: Smaller, more frequent changes</li>
              <li><strong>Better Collaboration</strong>: Developers and operations work together</li>
          </ul>
          
          <h4>AWS DevOps Services:</h4>
          <ul>
              <li><strong>CodeCommit</strong>: Managed Git repositories</li>
              <li><strong>CodeBuild</strong>: Build and test code</li>
              <li><strong>CodeDeploy</strong>: Deploy to various compute services</li>
              <li><strong>CodePipeline</strong>: Orchestrate CI/CD workflows</li>
              <li><strong>CodeStar</strong>: Unified project dashboard</li>
          </ul>
          
          <h4>Typical CI/CD Pipeline:</h4>
          <ol>
              <li><strong>Source Stage</strong>: CodeCommit, GitHub, Bitbucket</li>
              <li><strong>Build Stage</strong>: CodeBuild (compile, run tests)</li>
              <li><strong>Test Stage</strong>: Automated tests (unit, integration)</li>
              <li><strong>Deploy Stage</strong>: CodeDeploy (dev, staging, production)</li>
              <li><strong>Approval Stage</strong>: Manual approval before production</li>
          </ol>
          ''',
          'mini_tutorial': '''## 🎯 CI/CD Pipeline Fundamentals
📖 What You'll Learn:
Continuous Integration (CI) concepts

Continuous Delivery/Deployment (CD) concepts

AWS DevOps services overview

Pipeline design patterns

🔑 CI/CD Benefits:
Faster Releases: Automation reduces manual steps

Higher Quality: Automated testing catches bugs early

Reduced Risk: Smaller changes, easier rollbacks

Better Collaboration: Dev and Ops work together

🏗️ AWS DevOps Stack:
text
CodeCommit → CodeBuild → CodeDeploy → CloudFormation
     ↓           ↓           ↓             ↓
 Git Repo    Build/Test   Deployment   Infrastructure
⚠️ CI/CD Mistakes:
No automated testing in pipeline ❌

Manual steps in deployment ❌

No rollback strategy ❌

Not monitoring pipeline health ❌

✅ CI/CD Best Practices:
✅ Implement comprehensive automated testing

✅ Use infrastructure as code (CloudFormation/CDK)

✅ Implement blue-green deployments

✅ Monitor pipeline metrics and success rates

✅ Use feature flags for gradual rollouts

✅ Implement security scanning in pipeline

✅ Regularly review and optimize pipeline

🔄 Pipeline Stages:
Source: Code repository (CodeCommit, GitHub)

Build: Compile, run unit tests (CodeBuild)

Test: Integration, performance, security tests

Deploy: Staging environment (CodeDeploy)

Approval: Manual gate before production

Production: Final deployment

Post-Deploy: Smoke tests, monitoring

🛠️ AWS Code Services:
CodeCommit: Managed Git repositories

CodeBuild: Build and test service

CodeDeploy: Deployment automation

CodePipeline: Workflow orchestration

CodeStar: Project management dashboard

📈 Metrics to Monitor:
Build success/failure rate

Test coverage percentage

Deployment success rate

Mean time to recovery (MTTR)

Lead time for changes'''
},
{
'title': 'AWS CodePipeline',
'content': '''
<h3>CodePipeline: Orchestrate Release Pipelines</h3>

text
          <h4>Pipeline Components:</h4>
          <ul>
              <li><strong>Pipeline</strong>: Overall workflow definition</li>
              <li><strong>Stage</strong>: Logical group of actions (Source, Build, Deploy)</li>
              <li><strong>Action</strong>: Task performed in a stage (build, deploy, test)</li>
              <li><strong>Artifact</strong>: Output passed between stages</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create CodePipeline via CLI</h5>
              <pre><code class="language-bash">
Create S3 bucket for artifacts
aws s3 mb s3://my-codepipeline-artifacts-2024

Create pipeline
aws codepipeline create-pipeline \
--pipeline {
"name": "MyWebAppPipeline",
"roleArn": "arn:aws:iam::123456789012:role/AWSCodePipelineServiceRole",
"artifactStore": {
"type": "S3",
"location": "my-codepipeline-artifacts-2024"
},
"stages": [
{
"name": "Source",
"actions": [{
"name": "Source",
"actionTypeId": {
"category": "Source",
"owner": "AWS",
"version": "1",
"provider": "CodeCommit"
},
"configuration": {
"RepositoryName": "my-web-app",
"BranchName": "main"
},
"outputArtifacts": [{"name": "SourceOutput"}],
"runOrder": 1
}]
},
{
"name": "Build",
"actions": [{
"name": "Build",
"actionTypeId": {
"category": "Build",
"owner": "AWS",
"version": "1",
"provider": "CodeBuild"
},
"configuration": {
"ProjectName": "my-web-app-build"
},
"inputArtifacts": [{"name": "SourceOutput"}],
"outputArtifacts": [{"name": "BuildOutput"}],
"runOrder": 1
}]
}
]
}
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 CodePipeline - Workflow Orchestration

📖 What You'll Learn:
CodePipeline components and concepts

Pipeline design and configuration

Artifact management

Stage and action configuration

🔑 CodePipeline Components:
Pipeline: Overall workflow

Stage: Logical group (Source, Build, Deploy)

Action: Task within stage (build, test, deploy)

Artifact: Output passed between stages

Transition: Movement between stages

🏗️ Pipeline Architecture:
text
Source Stage → Build Stage → Test Stage → Deploy Stage
     ↓             ↓            ↓            ↓
CodeCommit    CodeBuild    Test Actions  CodeDeploy
GitHub       Unit Tests   Integration   Staging/Prod
⚠️ Pipeline Mistakes:
Too many manual approvals ❌

Not handling failed deployments ❌

No artifact versioning ❌

Complex pipeline logic ❌

✅ CodePipeline Best Practices:
✅ Use S3 for artifact storage (encrypted)

✅ Implement manual approval gates wisely

✅ Use parallel actions when possible

✅ Monitor pipeline execution with CloudWatch

✅ Implement pipeline notifications (SNS)

✅ Use variables and parameter store for configuration

✅ Regularly review and clean up old executions

🔧 Creating a Pipeline:
bash
aws codepipeline create-pipeline \
    --pipeline file://pipeline-definition.json
📦 Artifact Management:
S3 Bucket: Encrypted, versioned

Artifact Naming: Consistent naming convention

Retention: Clean up old artifacts

Security: IAM permissions, encryption

🚦 Stage Transitions:
Automatic: On successful completion

Manual: Approval required

Conditional: Based on variables

Parallel: Multiple actions simultaneously

🔔 Notifications:
SNS topics for pipeline events

Chat integrations (Slack, Teams)

Email notifications for failures

CloudWatch Events for automation

📊 Monitoring:
CloudWatch metrics for success rates

X-Ray tracing for performance

Custom dashboards for visibility

Automated alerts for failures'''
},
{
'title': 'AWS CodeBuild',
'content': '''
<h3>CodeBuild: Build and Test Code</h3>

text
          <h4>CodeBuild Components:</h4>
          <ul>
              <li><strong>Build Project</strong>: Configuration for builds</li>
              <li><strong>Build Spec</strong>: YAML file defining build commands</li>
              <li><strong>Environment</strong>: Compute resources and Docker image</li>
              <li><strong>Source</strong>: Where code comes from (CodeCommit, S3, GitHub)</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Sample buildspec.yml</h5>
              <pre><code class="language-yaml">
version: 0.2

phases:
install:
runtime-versions:
python: 3.9
commands:
- pip install -r requirements.txt

pre_build:
commands:
- python -m pytest tests/ --junitxml=test-results.xml

build:
commands:
- echo Build started on date
- docker build -t myapp:$CODEBUILD_RESOLVED_SOURCE_VERSION .

post_build:
commands:
- echo Build completed on date
- docker tag myapp:$CODEBUILD_RESOLVED_SOURCE_VERSION 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest

artifacts:
files:
- '**/*'
discard-paths: no

reports:
pytest_reports:
files:
- test-results.xml
file-format: JUNITXML
</code></pre>
</div>

text
            <div class="code-block">
                <h5><i class="fas fa-code"></i> Create CodeBuild Project</h5>
                <pre><code class="language-bash">
aws codebuild create-project \
--name "my-web-app-build" \
--source '{
"type": "CODECOMMIT",
"location": "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/my-web-app"
}' \
--artifacts '{
"type": "CODEPIPELINE"
}' \
--environment '{
"type": "LINUX_CONTAINER",
"image": "aws/codebuild/amazonlinux2-x86_64-standard:4.0",
"computeType": "BUILD_GENERAL1_SMALL",
"privilegedMode": true
}' \
--service-role "arn:aws:iam::123456789012:role/CodeBuildServiceRole"
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 CodeBuild - Automated Builds

📖 What You'll Learn:
CodeBuild project configuration

Build specification (buildspec.yml)

Environment and compute configuration

Build artifacts and reports

🔑 CodeBuild Components:
Build Project: Configuration (source, environment, artifacts)

Buildspec: YAML defining build steps

Environment: Compute type, Docker image, credentials

Source: Code location (CodeCommit, GitHub, S3)

Artifacts: Build output

🏗️ Build Process:
text
Source → Environment Setup → Build Phases → Artifacts/Reports
  ↓           ↓                ↓              ↓
Code      Docker Image    install → pre_build   S3/ECR
         Compute Type     → build → post_build
⚠️ Build Mistakes:
Builds taking too long ❌

No test reporting ❌

Large build artifacts ❌

No caching configuration ❌

✅ CodeBuild Best Practices:
✅ Use buildspec.yml for build definition

✅ Implement caching for dependencies

✅ Use reports for test results visualization

✅ Right-size compute type (cost vs speed)

✅ Use environment variables for configuration

✅ Monitor build metrics and logs

✅ Implement build timeouts

📝 Buildspec Structure:
yaml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.9
    commands:
      - pip install -r requirements.txt
  pre_build:
    commands:
      - run_tests.sh
  build:
    commands:
      - build_artifacts.sh
  post_build:
    commands:
      - package_artifacts.sh
artifacts:
  files:
    - '**/*'
  base-directory: 'dist'
reports:
  test_report:
    files:
      - 'test-results.xml'
    file-format: JUNITXML
cache:
  paths:
    - '/root/.cache/pip/**/*'
💰 Cost Optimization:
Use smaller compute types for dev builds

Implement caching for dependencies

Clean up old build artifacts

Use Spot Fleets for non-critical builds

Monitor build duration and costs

🧪 Test Integration:
JUnit XML reports for test results

Code coverage reports

Security scanning integration

Performance testing

Quality gates based on metrics

🔧 Creating a Build Project:
bash
aws codebuild create-project \
    --name "my-app-build" \
    --source type=CODECOMMIT,location=https://git-codecommit... \
    --artifacts type=CODEPIPELINE \
    --environment type=LINUX_CONTAINER,image=aws/codebuild/...,computeType=BUILD_GENERAL1_SMALL \
    --service-role arn:aws:iam::123456789012:role/CodeBuildServiceRole
```'''
            },
            {
                'title': 'AWS CodeDeploy',
                'content': '''
                <h3>CodeDeploy: Automated Deployments</h3>
                
                <h4>Deployment Types:</h4>
                <ul>
                    <li><strong>In-place</strong>: Update existing instances
                        <ul>
                            <li>Rolling update: Update batches of instances</li>
                            <li>All-at-once: Update all instances simultaneously</li>
                        </ul>
                    </li>
                    <li><strong>Blue/Green</strong>: Launch new environment, switch traffic
                        <ul>
                            <li>Zero downtime deployment</li>
                            <li>Easy rollback if issues occur</li>
                        </ul>
                    </li>
                </ul>
                
                <h4>CodeDeploy Components:</h4>
                <ul>
                    <li><strong>Application</strong>: Unique name for your application</li>
                    <li><strong>Deployment Group</strong>: Set of instances to deploy to</li>
                    <li><strong>Deployment Configuration</strong>: Rules for deployment</li>
                    <li><strong>AppSpec File</strong>: YAML defining deployment steps</li>
                </ul>
                
                <div class="code-block">
                    <h5><i class="fas fa-code"></i> Sample appspec.yml</h5>
                    <pre><code class="language-yaml">
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html
hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root
  AfterInstall:
    - location: scripts/start_server.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_server.sh
      timeout: 300
      runas: root
  ValidateService:
    - location: scripts/validate_service.sh
      timeout: 300
      runas: root
                    </code></pre>
                </div>
                ''',
                'mini_tutorial': '''## 🎯 CodeDeploy - Automated Deployments

### 📖 **What You'll Learn:**
- Deployment strategies (in-place vs blue/green)
- CodeDeploy components and configuration
- AppSpec file definition
- Deployment hooks and lifecycle events

### 🔑 **Deployment Strategies:**
1. **In-Place**: Update existing instances
   - Rolling: Batch updates
   - All-at-once: All instances simultaneously
2. **Blue/Green**: Launch new environment
   - Zero downtime
   - Easy rollback
   - Traffic shifting

### 🔑 **CodeDeploy Components:**
1. **Application**: Logical grouping
2. **Deployment Group**: Target instances
3. **Deployment Config**: Success/failure conditions
4. **AppSpec**: Deployment instructions
5. **Revision**: Application version

### 🏗️ **Deployment Process:**
Revision → Deployment → Lifecycle Hooks → Validation
↓ ↓ ↓ ↓
S3/ECR CodeDeploy BeforeInstall ValidateService
→ AfterInstall
→ ApplicationStart

text

### ⚠️ **Deployment Mistakes:**
- No health checks during deployment ❌
- Not testing rollback procedures ❌
- No deployment monitoring ❌
- Complex AppSpec files ❌

### ✅ **CodeDeploy Best Practices:**
1. ✅ **Use blue/green deployments for production**
2. ✅ **Implement comprehensive health checks**
3. ✅ **Monitor deployment metrics and logs**
4. ✅ **Use deployment configurations appropriate for your application**
5. ✅ **Test rollback procedures regularly**
6. ✅ **Use deployment groups for environment separation**
7. ✅ **Implement deployment notifications**

### 📋 **AppSpec Structure:**
```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html
hooks:
  BeforeInstall:
    - location: scripts/before_install.sh
      timeout: 300
  AfterInstall:
    - location: scripts/after_install.sh
      timeout: 300
  ApplicationStart:
    - location: scripts/start_server.sh
      timeout: 300
  ValidateService:
    - location: scripts/health_check.sh
      timeout: 300
🔄 Lifecycle Hooks:
BeforeInstall: Prepare environment

AfterInstall: Configure application

ApplicationStart: Start services

ValidateService: Verify deployment

BeforeAllowTraffic: Final checks (blue/green)

AfterAllowTraffic: Post-deployment tasks

🎯 Deployment Targets:
EC2/On-Premises: Traditional servers

ECS: Container services

Lambda: Serverless functions

AWS Lambda: Function updates

📊 Monitoring & Rollback:
CloudWatch alarms for deployment health

Automated rollback on failure

Deployment history and audit trails

Success/failure rate tracking

Mean time to recovery (MTTR) metrics'''
},
{
'title': 'Infrastructure as Code with CloudFormation',
'content': '''
<h3>AWS CloudFormation: Infrastructure as Code</h3>
<p>Model and provision AWS resources using templates.</p>

text
          <h4>CloudFormation Concepts:</h4>
          <ul>
              <li><strong>Template</strong>: JSON/YAML file describing AWS resources</li>
              <li><strong>Stack</strong>: Collection of resources created from template</li>
              <li><strong>Change Set</strong>: Preview changes before applying</li>
              <li><strong>Drift Detection</strong>: Detect manual changes to resources</li>
          </ul>
          
          <h4>Template Structure:</h4>
          <ul>
              <li><strong>AWSTemplateFormatVersion</strong>: Template version</li>
              <li><strong>Description</strong>: Template description</li>
              <li><strong>Parameters</strong>: Input values for template</li>
              <li><strong>Resources</strong>: AWS resources to create (required)</li>
              <li><strong>Outputs</strong>: Values to return after stack creation</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Sample CloudFormation Template</h5>
              <pre><code class="language-yaml">
AWSTemplateFormatVersion: '2010-09-09'
Description: Simple EC2 instance with security group

Parameters:
InstanceType:
Type: String
Default: t2.micro
AllowedValues:
- t2.micro
- t2.small
- t2.medium
Description: EC2 instance type

Resources:
WebServerSecurityGroup:
Type: AWS::EC2::SecurityGroup
Properties:
GroupDescription: Allow HTTP and SSH access
SecurityGroupIngress:
- IpProtocol: tcp
FromPort: 80
ToPort: 80
CidrIp: 0.0.0.0/0
- IpProtocol: tcp
FromPort: 22
ToPort: 22
CidrIp: 203.0.113.0/24

WebServerInstance:
Type: AWS::EC2::Instance
Properties:
InstanceType: !Ref InstanceType
ImageId: ami-0c55b159cbfafe1f0
SecurityGroupIds:
- !Ref WebServerSecurityGroup
Tags:
- Key: Name
Value: WebServer

Outputs:
InstanceId:
Description: Instance ID of the new EC2 instance
Value: !Ref WebServerInstance
PublicIP:
Description: Public IP address of the new EC2 instance
Value: !GetAtt WebServerInstance.PublicIp
</code></pre>
</div>

text
            <div class="code-block">
                <h5><i class="fas fa-code"></i> Deploy CloudFormation Stack</h5>
                <pre><code class="language-bash">
Create stack
aws cloudformation create-stack \
--stack-name WebAppStack \
--template-body file://template.yaml \
--parameters ParameterKey=InstanceType,ParameterValue=t2.micro \
--capabilities CAPABILITY_IAM

Update stack
aws cloudformation update-stack \
--stack-name WebAppStack \
--template-body file://template.yaml \
--parameters ParameterKey=InstanceType,ParameterValue=t2.small

Delete stack
aws cloudformation delete-stack --stack-name WebAppStack
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 CloudFormation - Infrastructure as Code

📖 What You'll Learn:
CloudFormation template structure

Stack creation and management

Change sets and drift detection

Best practices for IaC

🔑 CloudFormation Concepts:
Template: JSON/YAML defining resources

Stack: Collection of resources

Change Set: Preview of changes

Drift Detection: Manual changes detection

StackSet: Multi-region/account deployment

🏗️ Template Structure:
text
AWSTemplateFormatVersion
Description
Parameters (inputs)
Mappings (lookup tables)
Conditions (if/then)
Resources (required - AWS resources)
Outputs (return values)
⚠️ CloudFormation Mistakes:
Hardcoded values in templates ❌

No change set review ❌

Ignoring drift detection ❌

Complex nested stacks ❌

✅ CloudFormation Best Practices:
✅ Use YAML for readability

✅ Parameterize everything (no hardcodes)

✅ Use change sets before updates

✅ Enable drift detection

✅ Use nested stacks for complex architectures

✅ Implement stack policies for protection

✅ Monitor stack events and status

📝 Template Best Practices:
Use intrinsic functions (!Ref, !GetAtt, !Sub)

Implement conditions for environment differences

Use mappings for region-specific values

Add metadata and descriptions

Validate templates before deployment

🔄 Change Management:
Create Change Set: Preview changes

Review Changes: Understand impact

Execute Change Set: Apply changes

Monitor Deployment: Watch for errors

Rollback if Needed: Automatic on failure

🛡️ Stack Protection:
Stack policies (allow/deny updates)

Termination protection

Deletion policy (Retain, Delete, Snapshot)

Update policy (rolling updates, replacement)

🏢 Organizational IaC:
StackSets: Multi-account/region deployment

Service Catalog: Approved templates

Custom Resources: Extend CloudFormation

Macros: Transform templates

🔧 Deployment Workflow:
bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Create change set
aws cloudformation create-change-set \
    --stack-name MyStack \
    --change-set-name MyChangeSet \
    --template-body file://template.yaml \
    --parameters ParameterKey=InstanceType,ParameterValue=t2.micro

# Execute change set
aws cloudformation execute-change-set \
    --change-set-name MyChangeSet \
    --stack-name MyStack
📊 Monitoring & Governance:
CloudWatch alarms for stack events

Config rules for compliance

Cost allocation tags

Change approval workflows

Audit trails for all changes'''
}
]
},
{
'title': 'AWS Data Analytics',
'slug': 'aws-analytics',
'description': 'Process and analyze big data using AWS analytics services like S3, Glue, Athena, Redshift, and EMR.',
'difficulty': 'advanced',
'duration': 24,
'modules': [
{
'title': 'Amazon S3 for Data Lakes',
'content': '''
<h3>Building Data Lakes on Amazon S3</h3>

text
          <h4>Data Lake Architecture:</h4>
          <ul>
              <li><strong>Raw Zone</strong>: Store data in original format</li>
              <li><strong>Cleansed Zone</strong>: Processed and validated data</li>
              <li><strong>Curated Zone</strong>: Business-ready data (star schemas, aggregates)</li>
              <li><strong>Sandbox Zone</strong>: Experimental area for data scientists</li>
          </ul>
          
          <h4>S3 Data Lake Best Practices:</h4>
          <ul>
              <li>Use partitioned folders (s3://bucket/year=2024/month=01/)</li>
              <li>Choose appropriate storage classes (Standard, Intelligent-Tiering)</li>
              <li>Implement lifecycle policies for automatic data management</li>
              <li>Enable versioning for critical data</li>
              <li>Use S3 Inventory for tracking objects</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Organize S3 Data Lake</h5>
              <pre><code class="language-bash">
Create partitioned data structure
aws s3 mb s3://my-data-lake-2024

Create partitioned folders
aws s3api put-object --bucket my-data-lake-2024 --key raw/sales/year=2024/month=01/
aws s3api put-object --bucket my-data-lake-2024 --key raw/sales/year=2024/month=02/
aws s3api put-object --bucket my-data-lake-2024 --key cleansed/sales/year=2024/month=01/
aws s3api put-object --bucket my-data-lake-2024 --key curated/sales/daily_summary/

Upload sample data
aws s3 cp sales_202401.csv s3://my-data-lake-2024/raw/sales/year=2024/month=01/sales_202401.csv

Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
--bucket my-data-lake-2024 \
--lifecycle-configuration '{
"Rules": [{
"ID": "MoveToGlacierAfter90Days",
"Status": "Enabled",
"Prefix": "raw/",
"Transitions": [{
"Days": 90,
"StorageClass": "GLACIER"
}]
}]
}'
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 S3 Data Lakes - Foundation of Analytics

📖 What You'll Learn:
Data lake architecture and zones

S3 organization and partitioning

Storage classes and lifecycle management

Data lake security and governance

🔑 Data Lake Zones:
Raw Zone: Original, unprocessed data

Cleansed Zone: Validated, standardized data

Curated Zone: Business-ready datasets

Sandbox Zone: Experimental, research data

🏗️ Data Lake Architecture:
text
Data Sources → Ingestion → Raw Zone → Processing
     ↓           ↓           ↓           ↓
 Databases    Kinesis      S3 Raw     AWS Glue
   APIs       Firehose     (CSV/JSON)  EMR
                          → Cleansed Zone
                          → Curated Zone
⚠️ Data Lake Mistakes:
No schema enforcement ❌

Poor data organization ❌

No data quality checks ❌

Ignoring data governance ❌

✅ Data Lake Best Practices:
✅ Implement zone-based architecture

✅ Use partitioning for performance (date/category)

✅ Choose appropriate file formats (Parquet, ORC)

✅ Implement data catalog (Glue Data Catalog)

✅ Enable encryption and access controls

✅ Implement lifecycle policies for cost optimization

✅ Monitor data quality and lineage

📁 S3 Organization:
text
s3://data-lake/
├── raw/
│   ├── sales/year=2024/month=01/day=01/
│   ├── logs/year=2024/month=01/day=01/
│   └── events/year=2024/month=01/day=01/
├── cleansed/
│   ├── sales/year=2024/month=01/
│   └── events/year=2024/month=01/
├── curated/
│   ├── customer_360/
│   ├── sales_dashboard/
│   └── business_metrics/
└── sandbox/
    ├── data_science/
    └── analytics_poc/
💾 File Format Recommendations:
Analytics: Parquet or ORC (columnar, compressed)

Logs: JSON Lines or Avro

Archival: GZIP compressed CSV

Real-time: JSON or Avro

🔒 Security & Governance:
Bucket policies for access control

IAM roles for service access

Encryption (SSE-S3, SSE-KMS)

Access logging and monitoring

Data classification and tagging

💰 Cost Optimization:
S3 Intelligent-Tiering: Automatic storage class optimization

Lifecycle Policies: Move to cheaper storage over time

S3 Glacier: Archive infrequently accessed data

S3 Select: Query data without loading

Compression: Reduce storage and transfer costs'''
},
{
'title': 'Glue and Athena',
'content': '''
<h3>AWS Glue and Athena: Serverless Data Catalog and Query</h3>

text
          <h4>AWS Glue Components:</h4>
          <ul>
              <li><strong>Data Catalog</strong>: Central metadata repository</li>
              <li><strong>Crawlers</strong>: Automatically discover schema</li>
              <li><strong>Jobs</strong>: ETL (Extract, Transform, Load) processing</li>
              <li><strong>Workflows</strong>: Orchestrate multiple jobs</li>
          </ul>
          
          <h4>Amazon Athena:</h4>
          <p>Serverless interactive query service for S3 using standard SQL.</p>
          <ul>
              <li>Query data directly in S3</li>
              <li>Pay per query ($5 per TB scanned)</li>
              <li>Supports Parquet, ORC, JSON, CSV formats</li>
              <li>Integration with QuickSight for visualization</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create Glue Crawler and Query with Athena</h5>
              <pre><code class="language-bash">
Create Glue database
aws glue create-database \
--database-input '{"Name": "sales_database"}'

Create crawler
aws glue create-crawler \
--name sales-crawler \
--role arn:aws:iam::123456789012:role/AWSGlueServiceRole \
--database-name sales_database \
--targets '{"S3Targets": [{"Path": "s3://my-data-lake-2024/raw/sales/"}]}' \
--schedule "cron(0 1 * * ? *)" # Daily at 1 AM

Start crawler
aws glue start-crawler --name sales-crawler

Query with Athena (via CLI)
aws athena start-query-execution \
--query-string """
SELECT year, month, SUM(amount) as total_sales
FROM sales_database.sales
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month
""" \
--result-configuration '{"OutputLocation": "s3://my-data-lake-2024/query-results/"}'
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 Glue & Athena - Serverless Analytics

📖 What You'll Learn:
AWS Glue Data Catalog and crawlers

Glue ETL jobs and workflows

Athena query optimization

Serverless analytics architecture

🔑 AWS Glue Components:
Data Catalog: Central metadata store

Crawlers: Automatic schema discovery

ETL Jobs: Serverless Spark processing

Workflows: Job orchestration

Triggers: Event-based execution

🔑 Amazon Athena Features:
Serverless SQL queries on S3

Pay per query ($5/TB scanned)

Federated queries (RDS, DynamoDB)

Query result caching

JDBC/ODBC connectivity

🏗️ Serverless Analytics Architecture:
text
S3 Data → Glue Crawler → Data Catalog → Athena Query
   ↓          ↓             ↓             ↓
Raw Data  Schema Discovery  Metadata    Business
                          → Glue ETL   Intelligence
                          → Transform
⚠️ Analytics Mistakes:
No partitioning in S3 ❌

Scanning all data in Athena ❌

Complex Glue jobs ❌

No query optimization ❌

✅ Glue & Athena Best Practices:
✅ Use partitioned data in S3

✅ Compress data (Parquet/ORC)

✅ Use columnar formats for analytics

✅ Implement query result caching

✅ Monitor query costs and performance

✅ Use Glue bookmarks for incremental processing

✅ Implement data quality checks in ETL

📊 Query Optimization:
Partitioning: Filter by partition columns

Compression: Use Snappy with Parquet

Column Selection: SELECT only needed columns

File Size: Optimal 64MB-1GB files

Statistics: Gather table statistics

🔧 Glue ETL Job Example:
python
import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read from Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="sales_db",
    table_name="raw_sales"
)

# Transform data
cleaned = datasource.filter(
    lambda row: row["amount"] > 0 and row["customer_id"] is not None
)

# Write to curated zone
glueContext.write_dynamic_frame.from_options(
    frame=cleaned,
    connection_type="s3",
    connection_options={
        "path": "s3://data-lake/curated/sales/",
        "partitionKeys": ["year", "month"]
    },
    format="parquet"
)
💰 Cost Optimization:
Athena: Use partitioning, compression, columnar formats

Glue: Right-size DPUs, use job bookmarks

S3: Lifecycle policies, Intelligent-Tiering

Monitoring: CloudWatch metrics, cost alerts

📈 Performance Tuning:
DPU Allocation: 2-10 DPUs for Glue jobs

Parallelism: Adjust for data volume

Memory Management: Monitor Spark executors

Checkpointing: For long-running jobs'''
},
{
'title': 'Redshift Data Warehouse',
'content': '''
<h3>Amazon Redshift: Cloud Data Warehouse</h3>

text
          <h4>Redshift Architecture:</h4>
          <ul>
              <li><strong>Leader Node</strong>: Query planning and coordination</li>
              <li><strong>Compute Nodes</strong>: Execute queries and store data</li>
              <li><strong>Node Slices</strong>: Portion of node's memory and disk</li>
          </ul>
          
          <h4>Redshift Spectrum:</h4>
          <p>Query data directly in S3 without loading into Redshift.</p>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create Redshift Cluster</h5>
              <pre><code class="language-bash">
Create Redshift cluster
aws redshift create-cluster \
--cluster-identifier analytics-cluster \
--node-type dc2.large \
--master-username admin \
--master-user-password "SecurePass123!" \
--cluster-type multi-node \
--number-of-nodes 2 \
--publicly-accessible \
--iam-roles "arn:aws:iam::123456789012:role/RedshiftS3ReadRole"

Create table
aws redshift-data execute-statement \
--cluster-identifier analytics-cluster \
--database dev \
--db-user admin \
--sql """
CREATE TABLE sales_fact (
sale_id INTEGER,
product_id INTEGER,
customer_id INTEGER,
sale_date DATE,
amount DECIMAL(10,2),
region VARCHAR(50)
)
DISTKEY(customer_id)
SORTKEY(sale_date);
"""
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 Redshift - Cloud Data Warehouse

📖 What You'll Learn:
Redshift architecture and components

Table design (distribution and sort keys)

Redshift Spectrum for S3 queries

Performance optimization techniques

🔑 Redshift Architecture:
Leader Node: Query planning, coordination

Compute Nodes: Query execution, data storage

Node Slices: Parallel processing units

RA3 Nodes: Compute/storage separation

🔑 Redshift Features:
Spectrum: Query S3 directly

Concurrency Scaling: Automatic scaling for concurrent queries

Materialized Views: Pre-computed aggregates

AQUA: Hardware-accelerated cache

Data Sharing: Cross-cluster data access

🏗️ Redshift Architecture:
text
Leader Node → Compute Nodes → Node Slices
     ↓             ↓             ↓
Query Plan   Data Storage   Parallel
             Processing      Execution
             ↓
        Redshift Spectrum
             ↓
           S3 Data
⚠️ Redshift Mistakes:
Wrong distribution style ❌

No sort keys ❌

Large table scans ❌

No vacuum/analyze maintenance ❌

✅ Redshift Best Practices:
✅ Choose appropriate distribution style

KEY: Large fact tables (joins)

EVEN: Staging tables

ALL: Small dimension tables

✅ Use sort keys for range queries

✅ Implement compression encodings

✅ Use Spectrum for cold data

✅ Monitor query performance with System Tables

✅ Regularly run VACUUM and ANALYZE

✅ Implement workload management (WLM)

🗃️ Table Design:
sql
-- Fact table with distribution and sort keys
CREATE TABLE sales_fact (
    sale_id INTEGER,
    customer_id INTEGER DISTKEY,
    sale_date DATE SORTKEY,
    product_id INTEGER,
    amount DECIMAL(10,2),
    region VARCHAR(50)
)
DISTSTYLE KEY
SORTKEY (sale_date);

-- Dimension table with ALL distribution
CREATE TABLE customer_dim (
    customer_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(255),
    join_date DATE
)
DISTSTYLE ALL;
📊 Performance Optimization:
Distribution Style: Minimize data movement

Sort Keys: Range-restricted queries

Compression: Reduce storage, improve I/O

Query Tuning: Explain plans, system tables

Workload Management: Query queues, priorities

🔄 ETL Patterns:
COPY command: Bulk load from S3

UNLOAD command: Export to S3

Spectrum: Query external tables

Data Pipeline: Glue, DMS, or custom

💰 Cost Optimization:
RA3 nodes: Pay for compute, separate storage

Concurrency Scaling: Auto-scale for peak loads

Spectrum: Query cold data in S3

Reserved Instances: Steady-state workloads

Pause/Resume: For dev/test environments

🛠️ Maintenance:
VACUUM: Reclaim space, resort rows

ANALYZE: Update statistics

Deep Copy: Recreate tables (full resort)

System Table Monitoring: STL, STV tables'''
},
{
'title': 'EMR - Elastic MapReduce',
'content': '''
<h3>Amazon EMR: Big Data Processing</h3>

text
          <h4>EMR Components:</h4>
          <ul>
              <li><strong>Master Node</strong>: Manages the cluster</li>
              <li><strong>Core Nodes</strong>: Run tasks and store data in HDFS</li>
              <li><strong>Task Nodes</strong>: Optional, only run tasks</li>
          </ul>
          
          <h4>Supported Frameworks:</h4>
          <ul>
              <li><strong>Apache Spark</strong>: Fast cluster computing</li>
              <li><strong>Apache Hadoop</strong>: Distributed processing</li>
              <li><strong>Apache Hive</strong>: Data warehouse infrastructure</li>
              <li><strong>Presto</strong>: Distributed SQL query engine</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create EMR Cluster</h5>
              <pre><code class="language-bash">
Create EMR cluster
aws emr create-cluster \
--name "Spark Analytics Cluster" \
--release-label emr-6.9.0 \
--applications Name=Spark Name=Hive \
--ec2-attributes '{
"KeyName": "MyKeyPair",
"InstanceProfile": "EMR_EC2_DefaultRole",
"SubnetId": "subnet-abcdefgh",
"EmrManagedMasterSecurityGroup": "sg-master",
"EmrManagedSlaveSecurityGroup": "sg-slave"
}' \
--instance-groups '[
{
"Name": "Master nodes",
"Market": "ON_DEMAND",
"InstanceRole": "MASTER",
"InstanceType": "m5.xlarge",
"InstanceCount": 1
},
{
"Name": "Core nodes",
"Market": "ON_DEMAND",
"InstanceRole": "CORE",
"InstanceType": "m5.xlarge",
"InstanceCount": 2
}
]' \
--steps '[
{
"Name": "Setup debugging",
"ActionOnFailure": "TERMINATE_CLUSTER",
"HadoopJarStep": {
"Jar": "command-runner.jar",
"Args": ["state-pusher-script"]
}
}
]' \
--visible-to-all-users \
--service-role EMR_DefaultRole \
--auto-terminate
</code></pre>
</div>
''',
'mini_tutorial': '''## 🎯 EMR - Big Data Processing

📖 What You'll Learn:
EMR cluster architecture

Big data frameworks (Spark, Hadoop, Hive)

Cluster configuration and optimization

Cost management strategies

🔑 EMR Components:
Master Node: Cluster management, resource allocation

Core Nodes: Task execution, HDFS storage

Task Nodes: Optional, task execution only

Release: EMR version (6.9.0, etc.)

🔑 Supported Frameworks:
Apache Spark: Fast, in-memory processing

Apache Hadoop: MapReduce, HDFS

Apache Hive: SQL-like queries

Presto: Distributed SQL engine

HBase: NoSQL database

🏗️ EMR Architecture:
text
Master Node → Core Nodes → Task Nodes
     ↓           ↓            ↓
Cluster     Task Execution  Optional
Management  HDFS Storage    Scaling
YARN        Data Processing
⚠️ EMR Mistakes:
Over-provisioning clusters ❌

No auto-scaling ❌

Storing all data in HDFS ❌

Not monitoring cluster health ❌

✅ EMR Best Practices:
✅ Use Spot Instances for task nodes

✅ Implement auto-scaling for variable workloads

✅ Store data in S3 (not HDFS) when possible

✅ Use instance fleets for diverse instance types

✅ Monitor with CloudWatch metrics

✅ Use EMR Managed Scaling

✅ Terminate clusters when not in use

🚀 Spark Optimization:
Partitioning: Proper data partitioning

Caching: Reuse intermediate results

Broadcast Variables: Small datasets

Data Serialization: Kryo serialization

Memory Management: Driver/executor memory

💰 Cost Optimization:
Spot Instances: Up to 90% savings (task nodes)

Instance Fleets: Mix of instance types

Auto-scaling: Scale based on workload

S3 Storage: Instead of HDFS

Cluster Pausing: For interactive sessions

🔧 Spark Job Example:
python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("Sales Analysis") \
    .getOrCreate()

# Read from S3
df = spark.read.parquet("s3://data-lake/curated/sales/")

# Transform data
result = df \
    .filter(col("year") == 2024) \
    .groupBy("month", "product_category") \
    .agg(
        sum("amount").alias("total_sales"),
        count("*").alias("transaction_count")
    ) \
    .orderBy("month", "total_sales")

# Write to S3
result.write \
    .mode("overwrite") \
    .parquet("s3://data-lake/results/sales_summary/")
📊 Monitoring & Tuning:
Spark UI: Job monitoring, stages, tasks

Ganglia: Cluster metrics

CloudWatch: Custom metrics, alarms

YARN: Resource management

Logs: S3 or CloudWatch Logs

🛡️ Security:
IAM roles for EMR service and EC2 instances

Security groups for network isolation

Encryption at rest and in transit

Lake Formation integration for fine-grained access'''
},
{
'title': 'Kinesis for Real-time Streaming',
'content': '''
<h3>Amazon Kinesis: Real-time Data Streaming</h3>

text
          <h4>Kinesis Services:</h4>
          <ul>
              <li><strong>Kinesis Data Streams</strong>: Real-time data ingestion and processing</li>
              <li><strong>Kinesis Data Firehose</strong>: Load streaming data to destinations</li>
              <li><strong>Kinesis Data Analytics</strong>: Process streaming data with SQL</li>
              <li><strong>Kinesis Video Streams</strong>: Ingest and process video streams</li>
          </ul>
          
          <div class="code-block">
              <h5><i class="fas fa-code"></i> Create Kinesis Data Stream</h5>
              <pre><code class="language-bash">
Create data stream
aws kinesis create-stream \
--stream-name clickstream-data \
--shard-count 2

Put records
aws kinesis put-record \
--stream-name clickstream-data \
--data "{\"user_id\":\"123\",\"page\":\"home\",\"timestamp\":\"2024-01-15T10:30:00Z\"}" \
--partition-key user123

Create Firehose delivery stream
aws firehose create-delivery-stream \
--delivery-stream-name clickstream-to-s3 \
--delivery-stream-type DirectPut \
--s3-destination-configuration '{
"RoleARN": "arn:aws:iam::123456789012:role/firehose_delivery_role",
"BucketARN": "arn:aws:s3:::my-data-lake-2024",
"Prefix": "clickstream/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
"BufferingHints": {
"SizeInMBs": 64,
"IntervalInSeconds": 60
}
}'
</code></pre>
</div>

text
            <div class="tips mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
                <h5><i class="fas fa-lightbulb"></i> Analytics Architecture Pattern</h5>
                <p><strong>Real-time + Batch Analytics:</strong></p>
                <ol>
                    <li>Ingest real-time data with Kinesis Data Streams</li>
                    <li>Process real-time analytics with Kinesis Data Analytics</li>
                    <li>Store raw data in S3 via Kinesis Data Firehose</li>
                    <li>Run batch processing with Glue/EMR on historical data</li>
                    <li>Serve business queries with Athena/Redshift</li>
                </ol>
            </div>
            ''',
            'mini_tutorial': '''## 🎯 Kinesis - Real-time Streaming Analytics
📖 What You'll Learn:
Kinesis Data Streams for real-time ingestion

Kinesis Data Firehose for data delivery

Kinesis Data Analytics for stream processing

Real-time analytics architecture

🔑 Kinesis Services:
Data Streams: Real-time data ingestion (custom processing)

Data Firehose: Automatic delivery to destinations

Data Analytics: SQL-based stream processing

Video Streams: Video ingestion and processing

🏗️ Streaming Architecture:
text
Data Producers → Kinesis Data Streams → Consumers
      ↓                 ↓                  ↓
Web/Mobile       Shards (1MB/sec)     Lambda
IoT Devices      Partition Key        EMR
Applications                          Kinesis Analytics
                                     → Firehose → S3/Redshift
⚠️ Streaming Mistakes:
Wrong shard count estimation ❌

No error handling in consumers ❌

Not monitoring stream metrics ❌

Data loss during scaling ❌

✅ Kinesis Best Practices:
✅ Right-size shard count based on throughput

✅ Use partition keys for even distribution

✅ Implement checkpointing in consumers

✅ Monitor stream metrics (IncomingBytes, GetRecords)

✅ Use enhanced fan-out for high-throughput consumers

✅ Implement error handling and retries

✅ Use Firehose for simple ETL to destinations

📈 Shard Capacity Planning:
Write: 1MB/sec or 1000 records/sec per shard

Read: 2MB/sec per shard (standard)

Enhanced Fan-out: 2MB/sec per consumer

Partition Key: Even distribution across shards

🔄 Data Processing Patterns:
Lambda Consumer: Simple processing, low latency

Kinesis Analytics: SQL-based processing, windowing

EMR/Spark Streaming: Complex processing, stateful

Firehose: Simple ETL, automatic delivery

🔧 Kinesis Analytics Example:
sql
-- Create streaming source
CREATE OR REPLACE STREAM "CLICKSTREAM_SOURCE" (
    user_id VARCHAR(64),
    page VARCHAR(256),
    action VARCHAR(64),
    timestamp TIMESTAMP
);

-- Create in-application stream
CREATE OR REPLACE STREAM "CLICKSTREAM_DESTINATION" (
    user_id VARCHAR(64),
    page_views BIGINT,
    unique_pages BIGINT,
    window_time TIMESTAMP
);

-- Process data with sliding window
INSERT INTO "CLICKSTREAM_DESTINATION"
SELECT STREAM
    user_id,
    COUNT(*) AS page_views,
    COUNT(DISTINCT page) AS unique_pages,
    FLOOR(EVENT_TIME TO MINUTE) AS window_time
FROM "CLICKSTREAM_SOURCE"
WHERE action = 'page_view'
GROUP BY
    user_id,
    STEP("CLICKSTREAM_SOURCE".ROWTIME BY INTERVAL '1' MINUTE);
📊 Monitoring & Optimization:
CloudWatch Metrics: IncomingBytes, GetRecords, IteratorAge

Enhanced Monitoring: Per-shard metrics

Consumer Lag: Monitor iterator age

Throughput: Adjust shard count based on load

Error Rates: Failed records, retries

🛡️ Security & Compliance:
IAM roles for producers and consumers

Server-side encryption (SSE)

VPC endpoints for private access

Compliance with data retention policies

Audit logging with CloudTrail

💰 Cost Optimization:
Shard Hours: Right-size shard count

Enhanced Fan-out: Only when needed

Data Retention: Minimum required (24h-365d)

Firehose: For simple delivery use cases

Monitoring: Avoid over-provisioning'''
}
]
}
]

@bp.route('/')
@bp.route('/home')
def index():
    courses = Course.query.filter_by(is_published=True).order_by(Course.created_at.desc()).limit(6).all()
    return render_template('index.html', title='Home', courses=courses)


@bp.route('/courses')
def courses():
    page = request.args.get('page', 1, type=int)
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('search', '')

    query = Course.query.filter_by(is_published=True)

    if difficulty != 'all':
        query = query.filter_by(difficulty=difficulty)

    if search:
        query = query.filter(or_(
            Course.title.ilike(f'%{search}%'),
            Course.description.ilike(f'%{search}%')
        ))

    courses = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )

    return render_template(
        'courses/list.html',
        title='All Courses',
        courses=courses,
        current_difficulty=difficulty,
        search_query=search
    )


@bp.route('/course/<string:slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()

    # Check if user is enrolled
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        is_enrolled = enrollment is not None

    return render_template(
        'courses/detail.html',
        title=course.title,
        course=course,
        modules=modules,
        is_enrolled=is_enrolled
    )


@bp.route('/course/<string:slug>/enroll', methods=['POST'])
@login_required
def enroll_course(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()

    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()

    if existing:
        flash('You are already enrolled in this course!', 'info')
    else:
        enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f'Successfully enrolled in {course.title}!', 'success')

    return redirect(url_for('main.course_detail', slug=slug))


@bp.route('/course/<string:course_slug>/module/<int:module_id>')
@login_required
def module_detail(course_slug, module_id):
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    module = Module.query.filter_by(id=module_id, course_id=course.id).first_or_404()

    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()

    if not enrollment:
        flash('You need to enroll in this course first!', 'warning')
        return redirect(url_for('main.course_detail', slug=course_slug))

    # Mark as accessed
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module.id
    ).first()

    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=module.id)
        db.session.add(progress)

    progress.last_accessed = db.func.now()
    db.session.commit()

    # Get all modules for navigation
    all_modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()

    return render_template(
        'courses/module.html',
        title=module.title,
        course=course,
        module=module,
        all_modules=all_modules
    )


@bp.route('/module/<int:module_id>/complete', methods=['POST'])
@login_required
def mark_module_complete(module_id):
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()

    if progress:
        progress.completed = True
        db.session.commit()
        flash('Module marked as completed!', 'success')

    module = Module.query.get_or_404(module_id)
    return redirect(url_for(
        'main.module_detail',
        course_slug=module.course.slug,
        module_id=module_id
    ))


@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    # Get statistics
    total_courses = Course.query.count()
    total_users = User.query.count()
    total_enrollments = Enrollment.query.count()
    published_courses = Course.query.filter_by(is_published=True).count()
    total_modules = Module.query.count()

    # Get recent courses
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()

    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    stats = {
        'total_courses': total_courses,
        'total_users': total_users,
        'total_enrollments': total_enrollments,
        'published_courses': published_courses,
        'total_modules': total_modules,
        'completed_modules': UserProgress.query.filter_by(completed=True).count(),
        'active_users': User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(days=1)
        ).count()
    }

    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        stats=stats,
        recent_courses=recent_courses,
        recent_users=recent_users
    )


@bp.route('/admin/create-course', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        abort(403)

    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            slug=form.title.data.lower().replace(' ', '-'),
            description=form.description.data,
            difficulty=form.difficulty.data,
            duration_hours=int(form.duration_hours.data),
            is_published=True
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('main.courses'))

    return render_template('admin/course_form.html', form=form, title='Create Course')


@bp.app_context_processor
def inject_courses_data():
    def get_all_courses():
        return Course.query.filter_by(is_published=True).all()
    return dict(get_all_courses=get_all_courses)


def init_sample_data():
    """Initialize sample AWS courses and modules"""
    for course_data in AWS_COURSES_DATA:
        # Check if course already exists
        existing = Course.query.filter_by(slug=course_data['slug']).first()
        if not existing:
            course = Course(
                title=course_data['title'],
                slug=course_data['slug'],
                description=course_data['description'],
                difficulty=course_data['difficulty'],
                duration_hours=course_data['duration'],
                is_published=True
            )
            db.session.add(course)
            db.session.flush()  # Get the course ID

            # Add modules
            for i, module_data in enumerate(course_data['modules'], 1):
                module = Module(
                    title=module_data['title'],
                    content=module_data['content'],
                    mini_tutorial=module_data.get('mini_tutorial', ''),
                    order=i,
                    course_id=course.id
                )
                db.session.add(module)

    db.session.commit()
