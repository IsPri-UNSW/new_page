---
title: Robust multi-label surgical tool classification in noisy endoscopic videos

# Authors
# A YAML list of author names
# If you created a profile for a user (e.g. the default `admin` user at `content/authors/admin/`), 
# write the username (folder name) here, and it will be replaced with their full name and linked to their profile.
authors:
- Adnan Qayyum
- Hassan Ali
- Massimo Caputo
- Hunaid Vohra
- Taofeek Akinosho
- Sofiat Abioye
- Ilhem Berrou
- Paweł Capik
- Junaid Qadir
- Muhammad Bilal

# Author notes (such as 'Equal Contribution')
# A YAML list of notes for each author in the above `authors` list
author_notes: []

date: '2025-02-01'

# Date to publish webpage (NOT necessarily Bibtex publication's date).
publishDate: '2025-11-10T01:45:17.785078Z'

# Publication type.
# A single CSL publication type but formatted as a YAML list (for Hugo requirements).
publication_types:
- article-journal

# Publication name and optional abbreviated publication name.
publication: '*Scientific Reports*'
publication_short: ''

doi: 10.1038/s41598-024-82351-5

abstract: '<jats:title>Abstract</jats:title> <jats:p>Over the past few years, surgical
  data science has attracted substantial interest from the machine learning (ML) community.
  Various studies have demonstrated the efficacy of emerging ML techniques in analysing
  surgical data, particularly recordings of procedures, for digitising clinical and
  non-clinical functions like preoperative planning, context-aware decision-making,
  and operating skill assessment. However, this field is still in its infancy and
  lacks representative, well-annotated datasets for training robust models in intermediate
  ML tasks. Also, existing datasets suffer from inaccurate labels, hindering the development
  of reliable models. In this paper, we propose a systematic methodology for developing
  robust models for surgical tool classification using noisy endoscopic videos. Our
  methodology introduces two key innovations: (1) an intelligent active learning strategy
  for minimal dataset identification and label correction by human experts through
  collective intelligence; and (2) an assembling strategy for a student-teacher model-based
  self-training framework to achieve the robust classification of 14 surgical tools
  in a semi-supervised fashion. Furthermore, we employ strategies such as weighted
  data loaders and label smoothing to enable the models to learn difficult samples
  and address class imbalance issues. The proposed methodology achieves an average
  F1-score of 85.88% for the ensemble model-based self-training with class weights,
  and 80.88% without class weights for noisy tool labels. Also, our proposed method
  significantly outperforms existing approaches, which effectively demonstrates its
  effectiveness.</jats:p>'

# Summary. An optional shortened abstract.
summary: ''

tags: []

# Display this page in a list of Featured pages?
featured: false

# Links
url_pdf: ''
url_code: ''
url_dataset: ''
url_poster: ''
url_project: ''
url_slides: ''
url_source: ''
url_video: ''

# Custom links (uncomment lines below)
# links:
# - name: Custom Link
#   url: http://example.org

# Publication image
# Add an image named `featured.jpg/png` to your page's folder then add a caption below.
image:
  caption: ''
  focal_point: ''
  preview_only: false

# Associated Projects (optional).
#   Associate this publication with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects: ['internal-project']` links to `content/project/internal-project/index.md`.
#   Otherwise, set `projects: []`.
projects: []
links:
- name: URL
  url: https://doi.org/10.1038/s41598-024-82351-5
---


