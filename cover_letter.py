import json
import subprocess
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from models import Analysis, CompanyResearch,TopSkills,CoverLetter
import os
import re
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime


template = PromptTemplate.from_template("""

# About you

You are an expert cover letter writer. You excel at creating cover letters that are pleasant to read and create strong alignment with the job post. You are also a skilled writer, so when you craft a cover letter you don't simple repeat information from the job post but you create cohesive narratives that help the hiring team appreciate the talent of the candidate.

# Your task

Produce a tailored cover letter aligned with the job post and the resume. This letter will include
- An opening paragraph
- A Key strengths section
- A value alignment paragraph
- A closing paragraph

To craft this content, you will leverage the information in the job post, the analysis done on the job post, the talent background, and the identified relevant accomplishments from the talent's experience.

Your main strategy is to craft the cover letter is to focus on those job requirements that have strong alignment with the candidate background, combine 2 or three accomplishments and provide a narrative that focus on how the candidate can satisfy the job success criteria and help the company take advantage of the opportunities ahead or tackle the challenges it faces

# Context
The talent has over 15 years of experience, with a strong background in product management, solution engineering, and technology consulting. It balances strong and hands-on technical skills with strong business acumen. He has also successfully led customer engagements as a sales and technical leader.

Here are the talent's career highlights:
- Conceptualized, developed and launched a successful Generative AI product at 8base
- Integrated five enterprise products and expanded them with machine learning capabilities and process automation to create the Information Governance Suite at Everteam, leading to the company's acquisition by Kyocera
- Led the development and go-to-market execution of Intalio|Create, a CRM-based cloud development PaaS, leading to its acquisition by ServiceMax
- Managed multiple iterations of Intalio|BPMS, a process automation platform, leading to its acquisition by Everteam
- Subject matter expert in IT Architecture, Process Automation (BPM), Software Integrations, Low-Code platforms, and AI/ML capabilities
- Led technical presales efforts to enterprise customers in areas
- Combines hands-on technical skills with effective team leadership and successful customer engagements

Here's a mock interview done by the talent for you to get an understanding of the talent's background:



## Experience
Here's a list of the talent's most relevant accomplishments in the talent's past experience

### 8base - Director of Product Management / VP of Product Management
8base was a series A company that created low-code development tools for technical users. It had a backend-as-a-service platform that allowed users to create a GraphQL backend for their applications easily, and it was a low-code web app development tool for Javascript developers. Later, the company introduced Archie, a generative AI-powered platform to assist entrepreneurs, agencies, and product teams with the requirements to create digital products and the associated planning.

**Accomplishments**
```json
{eightBase_accomplishments}
```

### Appify - Director of Solution Engineering
Appify was a series A company with a low-code platform focused on field services operations

**Accomplishments**
```json
{appify_accomplishments}
```

### Everteam - Director of Product Management / VP of Solution Engineering / CTO

Everteam was a French-based company with a significant presence in EMEA, providing solutions for document management, content analytics, and records management. Everteam acquired Intalio in 2015

**Accomplishments**
```json
{everteam_accomplishments}
```

### Intalio - Senior Solution Consultant / Product Manager
Intalio was VC-backend company offering an open-source Business Process Management Suite called Intalio|BPMS. It also launched a CRM-based cloud development platform called Intalio|Create, that later sold its intellectual property to ServiceMax

**Accomplishments**
```json
{intalio_accomplishments}
```

# Instructions

- Anything you write needs to be factual against the information provided about the talent (background and accomplishments). You can't make up information.
- For the cover letter, follow these instructions:
	- **Opening Paragraph**: Capture attention enthusiastically and align yourself with the role and company. Write a compelling introduction that states the position you're applying for, highlights your relevant experience, and aligns with the company's goals or mission. Include why the company/role excites you. It should be 3 to five sentences long.
	- **Core Competencies Paragraph**: Highlight key core competencies and experiences that are key to achieve the success criteria. Summarize 3-5 key strengths or experiences tailored to the job description. You are encouraged to combine the most relevant accomplishments into a compelling narrative of the talent's core competencies alignment with the role. You can also incorporate elements provided in the mock interview.
	- **Value Alignment Paragraph** : Explain how the candidate can deliver significant impact to the company. While thinking, answer yourself (1) How will this role help the company address the challenges ahead?, (2) How will this role help this compay capitalize on the opportunities?. (3) What experiences and competencies does the candidate have that can reassure the reader this candidate is the best choice. Do not call out explicity challenges, opportunities or candidate experiences, but instead provide a narrative focused on the candidates competencies.
	- **Call-to-Action Paragraph** : Express enthusiasm for next steps and demonstrate eagerness to contribute. Thank the reader for their time, reiterate your interest, and invite a conversation about the role. It should be 2 to three sentences long.
- You should maximize the use of keywords from the analysis when writing the professional summary, key skills and accomplishments, and cover letter. However, those used should not read forced but fit naturally in the narrative.

# Cover letter samples
## Sample 1
### Sample Job post
```
##  About the job 
**About Anaconda  
******Be at the center of AI  
**** With more than 45 million users, Anaconda is the most popular operating system for AI providing access to the foundational open-source Python packages used in modern AI, data science, and machine learning through a seamless platform. We pioneered the use of Python for data science, championed its vibrant community, and continue to steward open-source projects that make tomorrow’s innovations possible. Our enterprise-grade solutions enable corporate, research, and academic institutions around the world to harness the power of open source for competitive advantage, groundbreaking research, and a better world. To learn more visit https://www.anaconda.com.  
Here is why people love most about working here: We’re not just a company, we’re part of a movement. Our dedicated employees and user community are democratizing data science and creating and promoting open-source technologies for a better world, and our commercial offerings make it possible for enterprise users to leverage the most innovative output from open source in a secure, governed way.  
**Summary  
** Anaconda is seeking a talented**** Sr. Technical Product Manager**** to drive the evolution of our Python Package Build Platform. This is an excellent opportunity for you to combine your expertise in platform design, automation, and AI tooling with your passion for data science and analytics  
**What You’ll Do  
**
  - Led the technical product roadmap for Anaconda’s Python Package Build Platform, focusing on automation, scalability, and integration with AI-driven tooling.
  - Collaborate with engineering teams to develop innovative automation and AI-powered solutions to advance platform capabilities.
  - Interact with customers, partners, and suppliers to understand requirements and drive product alignment with market needs.
  - Translate complex technical needs into clear, actionable product specifications and requirements.
  - Prioritize product improvements, feature requests, and bug fixes based on user feedback, business goals, and strategic impact.
  - Drive cross-functional collaboration with sales, marketing, UX, Anaconda Core, and operations to ensure seamless product delivery.
  - Analyze and resolve issues impacting the platform’s success autonomously and effectively.
  - Stay informed of industry trends, open-source developments, and competitive offerings to shape long-term product strategy  
**What You Need  
**
  - 8+ years of product management experience with a strong technical focus.
  - Deep understanding of how platforms work, including architecture, scalability, and integration.
  - Experience designing and implementing automation systems and AI tooling to streamline processes.
  - Demonstrated expertise in Python and open-source ecosystems, particularly in package building and management systems.
  - Familiarity with CI/CD pipelines and software lifecycle management.
  - Proven ability to operate effectively in a matrixed organization, coordinating across diverse teams.
  - Team attitude: “I am not done until WE are done”
  - Embody our core values:
    - Great People
    - Great Product
    - Great Performance
  - Care deeply about fostering an environment where people of all backgrounds and experiences can flourish   
**What Will Make You Stand Out  
**
  - Experience working in a fast-paced startup environment
  - Experience in an open-source or data science-focused company.
  - Strong background in package environment management or long-term supported product development.
  - Expertise in building tools that integrate automation and AI to solve technical challenges.  
```
### Cover letter
```
I am excited to apply for the Sr. Technical Product Manager role at Anaconda, Inc. With over 15 years of experience in product management, solution engineering, and technology consulting, I have developed strong technical skills combined with strategic product vision and a track record of launching AI-powered platforms and integrating automation into enterprise products. 

My career reflects a blend of strategic planning, technical innovation, and collaborative execution. To be able to deliver value in high-impact technical product roles, I relied on competencies like:
- Strategic Product Roadmap Development:  I have led the end-to-end development of comprehensive product roadmaps that translate complex technical requirements into actionable strategies. By aligning product visions with market demands, I have successfully driven initiatives from ideation to launch, ensuring that every step resonates with customer needs and business goals.
- Innovative AI and Automation Integration:  My work includes conceptualizing and launching AI-powered solutions that enhance product capabilities and streamline operations. Leveraging advanced AI methodologies and automation systems, I have optimized product performance and created impactful, scalable solutions in competitive environments.
- Cross-functional leadership and Collaboration:  I have a proven record of uniting diverse teams across engineering, design, marketing, and sales to execute product strategies. By fostering open communication and stakeholder engagement, I ensure that all aspects of the product lifecycle are aligned, driving both efficiency and innovation.

Anaconda’s success relies on evolving its platform to meet open-source governance and enterprise AI demands. I would address these challenges by leveraging my expertise in automation and AI, gained from leading machine learning initiatives and scaling enterprise platforms. Furthermore, Anaconda can enhance its market presence by providing innovative, Python-focused solutions for data science teams around the globe. My background in unifying cross-functional teams and delivering AI-driven enhancements positions me to boost platform performance, ensure secure package management, and speed up new feature delivery. I am confident that my execution of strategic roadmaps and technical leadership will help Anaconda meet current demands and shape the future of open-source data science.

Thank you for considering my application. I am excited to discuss how my background and skills can contribute to Anaconda's continued success, and I look forward to speaking with you soon.
                                       ```
```
## Sample 2
### Sample Job post
```
At point.me, we’re on a mission to increase the spending power for millions of people by turning loyalty points into powerful currency. To achieve this vision, we are seeking an experienced Senior Product Manager to lead and elevate our flight search experiences. In this role, you will leverage a deep understanding of customer needs, industry trends, and data-driven insights to design and deliver exceptional search features that drive user satisfaction and revenue growth.  
What You'll Do  
  - Enhance Flight Search Features: Own and continuously improve our flight search experience to align with customer expectations and business goals. Identify and prioritize opportunities to introduce innovative product features and new revenue streams within the search experience.
  - Performance Metrics: Define and track key performance metrics to measure success and inform feature requirements.
  - Product Strategy and Execution: Drive the end-to-end product development lifecycle, from defining the vision and roadmap to executing prototypes and measuring success at scale.
  - Launch 0-1 Features: Develop and scale in-app and email search alerts to engage users effectively and improve retention rates.
  - Optimize Features: Develop and execute an A/B testing strategy to optimize features, validate hypotheses, and deliver measurable impact.
  - Cross-Functional Collaboration: Work closely with the loyalty team to define business logic, success criteria, and priorities for search features, ensuring alignment with broader engineering and organizational initiatives. Collaborate with engineering, design, sales, and marketing teams to influence new business opportunities and drive the partner agenda.
  - Stakeholder Communication: Provide transparency and foster collaboration across teams through excellent communication skills, influencing without authority in complex stakeholder environments.  
Who You Are  
  - Product Management: 5+ years of experience as a Product Manager, with a proven track record of delivering impactful product features.
  - Search Product Expertise: 2+ years of experience working on a search product, demonstrating expertise in search technologies, personalization, and user experience.
  - Data-Driven: 2+ years of experience with data analysis, capable of deriving actionable insights and driving data-informed decision-making. You have the ability to use data to monitor metrics, define success, and identify gaps.
  - Entrepreneurial: Proven experience working with tech teams in high-growth startup environments, demonstrating extreme ownership and prioritizing ruthlessly to achieve organizational goals.
  - Problem Solver: Strong ability to break down complex problems into actionable steps, guide products from conception to launch, and measure success throughout the product lifecycle.
  - Passionately Curious: You are deeply passionate about delivering exceptional customer experiences through innovative travel search solutions, and are deeply curious about how this functionality fits into the broader product roadmap.
  - Collaborative Leader: You bring a collaborative mindset, capable of working cross-functionally and influencing technical and non-technical stakeholders at all levels.
  - Strategic: You have a strategic approach to defining vision and success while executing with precision at scale.  
This is a unique opportunity to shape the future of our flight search experiences, drive business growth, and make a meaningful impact on our users. If this sounds like you, we’d love to hear from you!  
**About Point.me  
** At point.me, we are committed to simplifying the loyalty points experience and increasing our customers' spending power by helping them see their points as currency. Join us and be part of a fast-growing company where your work will make a real impact. We offer competitive salaries, meaningful equity, comprehensive health coverage, and the opportunity to work fully remotely as part of a distributed team.  
Benefits & perks  
Join Our Growing Team! Here At Point.me We Believe In Taking Care Of Our Team, So That Our Team Can Take Care Of Our Customers. All Employees Are Offered The Following  
  - Competitive salaries and meaningful equity
  - Comprehensive health care coverage
  - A 100% distributed workforce, so you can contribute from wherever you prefer
  - An open vacation policy, with a minimum of 15 days off each year
  - Team trips and outings  
This is a management role, with commensurate responsibility and compensation. The anticipated salary range is $150,000 to $210,000. Specific compensation will be determined based on your level of experience.  
Given the nature of our business, we anticipate that all team members will be traveling from time to time, including company trips and off-sites, or meeting with strategic partners. As such, being fully vaccinated against COVID-19 is a condition of employment at point.me. We’ll ask you to send us a copy of your vaccination card in advance of your first day.  
While our team members can participate from anywhere, all applicants must be eligible to work in the United States.  
We respect the individual needs of employees and are an equal opportunity employer.
```
### Cover letter
```
I am thrilled to apply for the Senior Product Manager, Search position at point.me. With over 15 years of experience in product management, solution engineering, and technology consulting, I have consistently orchestrated data-driven innovations that deliver exceptional user experiences. I’m drawn by point.me’s mission to transform reward points into valuable currency, and I believe my track record of building scalable, customer-centric solutions will contribute meaningfully to your continued success.

My background combines deep technical fluency with strategic business insight. Below are several core strengths that align closely with driving product excellence in search and related technologies:

- Data-Driven Product Development: I have repeatedly utilized performance metrics and customer analytics to inform roadmap decisions, as seen when I aligned cross-functional teams around data tools like FullStory and Amplitude. This results-oriented mindset has helped me iterate quickly on product capabilities, boost adoption rates, and validate hypotheses using measurable outcomes.
- AI and Search Integration: At Everteam, I led the integration of multiple enterprise products with Apache Solr-powered indexing and search, NLP metadata extraction, and content classification. I improved search efficiency and user engagement by leveraging ML-driven technology—expertise that can elevate point.me’s flight search experiences in a similarly innovative way.
- 0-1 Feature Launch and Execution: From overseeing the launch of an AI-powered product at 8base to delivering iterative enhancements for enterprise platforms, I excel at shepherding new offerings from concept to market readiness. My approach emphasizes rapid prototyping, rigorous prioritization, and precise user-centric requirements to achieve early momentum and long-term growth.
- Cross-Functional Collaboration: I have unified globally dispersed product, engineering, and design teams to deliver complex solutions on time. By promoting open communication and leveraging stakeholder feedback, I ensure that every iteration aligns with technical feasibility and strategic objectives, fostering a collaborative environment that speeds up development cycles.

I am passionate about delivering innovative search experiences that expand travel options and simplify the customer journey. By focusing on clear metrics and iterative experiments, I can help point.me push the boundaries of personalization and discoverability for loyalty travelers. Drawing from my previous successes in AI-driven product design, I will leverage a structured approach to optimizing every aspect of the flight search experience—from real-time data synchronization to intuitive user flows. Furthermore, my experience in managing stakeholder communication equips me to navigate complex partner requirements and align teams around a shared roadmap vision. I am committed to moving swiftly to capture new opportunities while consistently driving measurable results that build trust with both customers and stakeholders.

Thank you for considering my application. I would like to discuss further how my experience and passion for data-informed product management can accelerate point.me’s mission and elevate the flight search experience for your users.

```
## Sample 3
### Sample Job post
```
** We are passionate about delivering high-quality, actionable data to solve real-world challenges in the home services industry. As businesses increasingly rely  
We are driven to solve real-world challenges in the home services industry with innovative, AI-powered solutions. As the industry evolves, we seek AI-focused Product Managers who thrive on change and build adaptable, intelligent products. Leveraging TitanIntelligence (TI), our branded AI, we transform data into actionable insights, automation, and decision intelligence that enhance efficiency and performance. Working closely with Product Managers and business stakeholders, we uncover new opportunities to modernize operations, optimize workflows, and help customers lead in their markets.  
**Principal TI Data Product Manager   
**The Principal TI Data Product Manager is a strategic and hands-on role, responsible for leading AI innovation by identifying opportunities and collaborating with Product Managers and Engineering to prototype and launch AI-driven solutions for real-world challenges. This role requires a strong ability to identify AI opportunities within business processes and to develop complex models into intelligent, scalable solutions with significant impact. Additionally, this role bridges traditional product management, AI engineering, and business strategy to deliver cutting-edge AI solutions that leverage the latest advancements to transform decision-making, automation, and operational efficiency, driving measurable business outcomes.  
**As a Principal TI Data Product Manager, you will:   
**
  - Spearhead the design and implementation of AI-driven data strategies that align with current business objectives and anticipate future needs.
  - Identify and translate AI and machine learning models into scalable enterprise solutions.
  - Collaborate with cross-functional teams, including Engineering, Customer Success, Product, Legal, and UX, to develop AI solutions that enhance user experience and operational efficiency.
  - Design and assess experiments focused on feature development, AI adoption, and data-driven decision-making to optimize outcomes.
  - Partner with business stakeholders to offer expertise in AI experimentation, causal inference, and model evaluation, utilizing methods like A/B testing, multivariate testing, and uplift modeling.
  - Define, prototype, and validate ML and AI solutions, ensuring feasibility and impact.
  - Define model requirements, encompassing functional specifications for LLMs, retrieval augmentation, prompt engineering, and AI-powered automation.
  - Work with prospects and customers to identify AI-driven business needs, pinpoint challenges, and showcase capabilities.
  - Stay ahead of AI advancements by leveraging techniques such as LLM fine-tuning, retrieval optimization, model customization, and AI performance evaluation.  
****To be successful in this role, you'll need:   
****
  - Passion for building AI-driven products that deliver measurable business impact.
  - Experience in AI applications across Fintech, Marketing, or other data-intensive industries.
  - A 4-year degree (or equivalent experience) in Computer Science, Engineering, Mathematics, or a related discipline.
  - 5+ years of experience in two or more of the following areas:  
    - AI & Machine Learning Product Development
    - AI Experimentation & Model Evaluation
    - Technical Product Management or AI Product Management
    - Data Science & Analytics
  - Strong verbal and written communication skills, with experience influencing cross-functional teams.
  - An entrepreneurial mindset with the ability to work independently and drive AI initiatives.
  - Familiarity with LLM agents, AI-powered automation, model governance, and responsible AI practices.
  - Experience developing and launching AI-driven products within enterprise environments.
  - Hands-on experience with query languages (SQL preferred) and tools such as Tableau, Snowflake, Azure, Pendo, and FullStory.
  - Experience in Home Services trades (HVAC, Plumbing, Electrical) is a plus.  
****Ways to Stand Out:  
****
  - Ability to simplify complex AI concepts into actionable insights for cross-functional teams.
  - Hands-on experience with LLM fine-tuning, AI retrieval systems, and advanced AI modeling.  
```
### Cover letter
```
I am excited to apply for the Principal Product Manager (Titan Intelligence) role at ServiceTitan. With more than 15 years in product management and AI-focused innovation, I bring a blend of technical expertise and practical leadership. ServiceTitan’s mission to modernize home services with AI aligns perfectly with my passion for creating impactful, data-driven solutions.

In my experience leading AI products, I have always focused on clear user benefits, cross-functional alignment, and measurable outcomes. Below are a few core areas where I excel and can contribute to ServiceTitan’s Titan Intelligence initiatives:

 - AI-Driven Product Leadership: I led teams to develop and launch machine learning features, focusing on real-world impact and easy adoption. By aligning technical possibilities with user needs, I ensured each release delivered measurable value.
 - Data-Informed Strategy: I use metrics and user feedback to shape product priorities, validate hypotheses, and optimize feature performance. This approach helps teams deliver meaningful improvements in rapid, iterative cycles.
- Scalable Solutions: At previous companies, I integrated multiple systems into unified platforms to handle growing data demands. This experience helps me design architectures that support AI expansion without compromising reliability or user experience.

My background in AI innovation can help ServiceTitan deliver automated insights and workflows that reduce manual tasks and enhance productivity. I believe in a practical approach, ensuring new features are easy to adopt and deliver immediate value for home services professionals. By championing data-driven experimentation, I can help refine AI features so they truly meet users’ evolving needs. With strong cross-functional collaboration, I will unify teams around common goals, speed up delivery cycles, and build trust with customers. My aim is to support ServiceTitan in its mission to transform this industry and empower every contractor with intelligent, user-friendly tools.

Thank you for reviewing my application. I look forward to discussing how my AI-focused expertise can advance Titan Intelligence and support ServiceTitan’s growth.

```
                                        
## Sample 4
### Sample Job post
```
##  About the job 
**What We Do:   
**At Autura, we're revolutionizing the towing and recovery industry with cutting-edge software that makes a real difference for our customers. From towing service providers to local governments, our tools—like Towing Management Systems, ARIES Dispatch, and Impound solutions—are designed to simplify operations, boost safety, and drive success. Joining Autura means being part of a team that's passionate about innovation, collaboration, and making the world a little safer and smarter every day. Ready to help us pave the way?  
**About the Role:   
**The Director of Product Management will be responsible for the development and success of the Private Towing segment of our portfolio, primarily focused on TMSs (Towing Management System). This individual will own the roadmap, prioritize features, and guide the product lifecycle from ideation to launch and beyond.   
This is a player-coach role and will mentor and grow two other Product Managers focused on private towing operators. The ideal candidate will have a deep understanding of product management, experience in developing software solutions, and a passion for delivering value to customers through intuitive and impactful products, while positively influencing direct reports and the broader team.   
**What You'll Be Doing:   
**
  - Shape and ensure the delivery of the roadmap for multiple Towing Management Systems
  - Collaborate with cross-functional teams, including engineering, design, sales, and marketing, to drive the development and launch of product features
  - Gather and analyze customer feedback and market trends to inform product decisions and identify new opportunities for growth and improvement
  - Define and understand product requirements, ensuring investments create measurable value
  - Manage the product lifecycle, including product release plans, timelines, and post-launch analysis to ensure continuous improvement
  - Monitor product performance using key metrics and adjust strategies as needed to meet objectives
  - Communicate product plans, progress, and results to stakeholders and senior management
  - Engage with customers and users to understand their needs and incorporate their feedback into the product development process
  - Champion user-centric design and advocate for the best user experience throughout the product development cycle   
**About You:   
**
  - 5+ years of experience as a Product Manager, preferably in the towing, transportation, or field services industries
  - Proven ability to manage and deliver software products from concept to launch
  - Technical acumen with an understanding of software development processes
  - Excellent analytical skills and the ability to make data-informed decisions
  - Outstanding communication and collaboration skills to work effectively with cross-functional teams
  - Experience equipping software development teams with the information they need to be successful
  - Ability to prioritize tasks and manage multiple projects in a fast-paced environment
  - Familiarity with agile development methodologies and tools
  - Bias for action and appreciation for in-person customer visits and discovery
  - Passion for user experience and building customer-centric products   
```
### Cover letter
```
I am excited to apply for the Director, Product Manager role at Autura. With over 15 years of experience in product management, solution engineering, and technology consulting, I have consistently driven successful software product strategies and lifecycle management initiatives. 

In my career, I have built a robust foundation in strategic product vision and execution by leveraging data-driven insights and fostering strong cross-functional partnerships. I have led product initiatives from concept to market launch, consistently delivering measurable results. My experience spans comprehensive product road mapping, integrating advanced technology solutions, and optimizing operational efficiency. These core competencies have driven customer-centric innovations and mentored teams to achieve excellence.

- Strategic Product Roadmapping & Lifecycle Management: I have defined and executed roadmaps aligned with market trends and customer needs, managing the product lifecycle from ideation to improvement. My planning skills and analytical decision-making prioritize key features and optimize resources. I have led successful product launches that exceeded performance metrics and customer expectations, delivering long-term value in fast-paced, evolving industries.
- Cross-Functional Leadership & Collaboration: I excel in collaborating with engineering, design, marketing, and sales teams for effective product development. My strong stakeholder engagement and agile methodology expertise enhance communication and alignment. By fostering collaboration, I accelerate product delivery and improve team performance, ensuring strategic objectives are met and driving innovation.
- Customer-Centric Innovation: I design products that prioritize customer needs by merging feedback with market trends, leading to intuitive and impactful user experiences. This focus on user-centric design boosts adoption rates and satisfaction, reflecting my commitment to solutions that tackle real-world challenges.

Autura’s vision to transform the towing industry with innovative software aligns with my background. My experience in managing product lifecycles and leading teams allows me to turn market insights and customer feedback into actionable strategies. I combine technical skills with a customer focus to ensure each product decision adds measurable value. By leveraging my expertise in agile management, I can help Autura adapt to industry changes and seize new opportunities

Thank you for considering my application. I am excited about the opportunity to contribute to Autura’s continued growth and innovation, and I welcome the chance to discuss my candidacy further. I look forward to the possibility of joining your team and driving forward impactful product strategies.


```
---                          
# Job Post

```text
{job_post}
```
# Analysis

```json
{analysis}
```
# Company

```json
{company}
```

# Matching the job post requirements with the candidate key skills and core competencies
The following are the key skills required in the job post matched with the candidate skill or core competency that is represented among the accomplishments
```json
{key_skills}
```

# Format instructions


{format_instructions}

Reply only with the JSON document that follows the provided schema. Do not add preamble or commentary.


# Quality checks

These are quality checks that you MUST satisfy:

- All the written information is factual and based on the information provided by the talent.
- The cover letter is based on the key matched skills of core competencies of the candidate
- The cover letter opening paragraph is 3 to 5 sentences long.
- The cover letter core competencies section has 3 to 5 key strengths or experiences.
- The strengths or experiences highlighted in the cover letter are not repeated in the resume.
- The cover letter value alignment paragraph is 4 to 6 sentences long.
- The cover letter call to action paragraph is 2 to 3 sentences long.
- The cover letter use the same tone, style and sentence structure from the provided samples.

""")


output_parser = JsonOutputParser(pydantic_object=CoverLetter)


def format_accomplishments(accomplishments,job):
    return [ {
            "accomplishment": f'{o["title"]}: {o["body"]}',
            "skills": o["skills"],
            "core_competencies": o["core_competencies"]
            } for o in accomplishments["accomplishments"][job] ]

def get_cover_letter_prompt():

    # Read input/01_job_post.txt as job_post
    with open('inputs/01_job_post.txt', 'r') as file:
        job_post = file.read()

    # read 02_analysis_result.json as Analysis
    with open('inputs/02_analysis_result.json', 'r') as file:
        data = json.load(file)
        analysis_result = Analysis(**data)

    # read 03_accomplishments.json as accomplishments
    with open('inputs/03_accomplishments.json', 'r') as file:
        accomplishments = json.load(file)

    # read 05_key_skills.json as key_skills
    with open('inputs/05_key_skills.json', 'r') as file:
        data = json.load(file)
        key_skills = TopSkills(**data)

    # read 06_company_data.json as company
    with open('inputs/07_company_data.json', 'r') as file:
        data = json.load(file)
        company = CompanyResearch(**data)

    eightBase_accomplishments = format_accomplishments(accomplishments,"8base")
    appify_accomplishments = format_accomplishments(accomplishments,"Appify")
    everteam_accomplishments = format_accomplishments(accomplishments,"Everteam")
    intalio_accomplishments = format_accomplishments(accomplishments,"Intalio")

    prompt = template.format(
        job_post=job_post,
        analysis=json.dumps(analysis_result.model_dump(),indent=4),
        company=json.dumps(company.model_dump(),indent=4),
        key_skills=json.dumps(key_skills.model_dump(),indent=4),
        eightBase_accomplishments=json.dumps(eightBase_accomplishments,indent=4),
        appify_accomplishments=json.dumps(appify_accomplishments,indent=4),
        everteam_accomplishments=json.dumps(everteam_accomplishments,indent=4),
        intalio_accomplishments=json.dumps(intalio_accomplishments,indent=4),
        format_instructions=output_parser.get_format_instructions())

    # write the prompt to a file called prompts/prompt_01.txt
    with open('prompts/cover_letter.md', 'w') as file:
        file.write(prompt)


def sanitize_filename(filename):
    """
    Sanitizes a string to be used as a valid filename.
    Removes invalid characters and replaces whitespaces with underscores.

    :param filename: The original string to sanitize.
    :return: A sanitized string safe for use as a filename.
    """
    # Remove invalid characters (anything except alphanumerics, dots, underscores, and hyphens)
    sanitized = re.sub(r'[^\w.\-]', '', filename)
    # Replace any sequence of whitespace with an underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized


def render_cover():

    clipboard_content = subprocess.check_output(['pbpaste']).decode('utf-8')
    cover_data = json.loads(clipboard_content)
    with open('inputs/08_cover_letter_data.json', 'w') as file:
        json.dump(cover_data, file, indent=4)    

    # read 02_analysis_result.json as Analysis
    with open('inputs/02_analysis_result.json', 'r') as file:
        data = json.load(file)
        analysis_data = Analysis(**data)



    folder_name = sanitize_filename(f"{analysis_data.company_name}-{analysis_data.job_title}")
    store_path = "/Users/estebanf/Library/CloudStorage/GoogleDrive-esteban.felipe@gmail.com/My Drive/JH 2025"

    # create document for cover letter
    cover = Document("cover.docx")

    for paragraph in cover.paragraphs:
        if '{{content}}' in paragraph.text:
            style = paragraph.style
            paragraph.text = cover_data['opening_paragraph'] + "\n"
            current_paragraph = paragraph
            core_competencies_paragraph = cover.add_paragraph()
            core_competencies_paragraph.style = style
            core_competencies_paragraph.text = cover_data['core_competencies_paragraph']['intro_paragraph'] + '\n'
            current_paragraph._p.addnext(core_competencies_paragraph._p)
            current_paragraph = core_competencies_paragraph
            items_paragraph = cover.add_paragraph()
            items_paragraph.style = style
            current_paragraph._p.addnext(items_paragraph._p)
            current_paragraph = items_paragraph

            for item in cover_data['core_competencies_paragraph']['core_competencies']:        # Add bullet point
                p = current_paragraph._element
                pPr = p.get_or_add_pPr()
                numPr = OxmlElement('w:numPr')
                ilvl = OxmlElement('w:ilvl')
                ilvl.set(qn('w:val'), "0")
                numId = OxmlElement('w:numId')
                numId.set(qn('w:val'), "2")
                numPr.append(ilvl)
                numPr.append(numId)
                pPr.append(numPr)
                
                # Add label in bold
                run = current_paragraph.add_run(f"{item['title']}: ")
                run.bold = True
                
                # Add details
                current_paragraph.add_run(item['details'])
                
                # Insert new paragraph after the current one
                new_paragraph = cover.add_paragraph()
                new_paragraph.style = style
                current_paragraph._p.addnext(new_paragraph._p)
                current_paragraph = new_paragraph
                
            current_paragraph.text = "\n" + cover_data['value_alignment_paragraph'] + "\n"
            call_to_action_paragraph = cover.add_paragraph()
            call_to_action_paragraph.style = style
            call_to_action_paragraph.text = cover_data['call_to_action_paragraph']
            current_paragraph._p.addnext(call_to_action_paragraph._p)

    savepath_cover = sanitize_filename(f"Esteban_Felipe-{analysis_data.company_name}-COVER.docx")
    # Save the file in the created folder
    cover.save(os.path.join(store_path, folder_name, savepath_cover))

