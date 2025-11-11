---
title: What is the Cost of Differential Privacy for Deep Learning-Based Trajectory
  Generation?

# Authors
# A YAML list of author names
# If you created a profile for a user (e.g. the default `admin` user at `content/authors/admin/`), 
# write the username (folder name) here, and it will be replaced with their full name and linked to their profile.
authors:
- Erik Buchholz
- Natasha Fernandes
- David D. Nguyen
- Alsharif Abuadbba
- Surya Nepal
- Salil S. Kanhere

# Author notes (such as 'Equal Contribution')
# A YAML list of notes for each author in the above `authors` list
author_notes: []

date: '2025-06-01'

# Date to publish webpage (NOT necessarily Bibtex publication's date).
publishDate: '2025-11-11T03:05:38.252501Z'

# Publication type.
# A single CSL publication type but formatted as a YAML list (for Hugo requirements).
publication_types:
- manuscript

# Publication name and optional abbreviated publication name.
publication: ''
publication_short: ''

doi: 10.48550/arxiv.2506.09312

abstract: While location trajectories offer valuable insights, they also reveal sensitive
  personal information. Differential Privacy (DP) offers formal protection, but achieving
  a favourable utility-privacy trade-off remains challenging. Recent works explore
  deep learning-based generative models to produce synthetic trajectories. However,
  current models lack formal privacy guarantees and rely on conditional information
  derived from real data during generation. This work investigates the utility cost
  of enforcing DP in such models, addressing three research questions across two datasets
  and eleven utility metrics. (1) We evaluate how DP-SGD, the standard DP training
  method for deep learning, affects the utility of state-of-the-art generative models.
  (2) Since DP-SGD is limited to unconditional models, we propose a novel DP mechanism
  for conditional generation that provides formal guarantees and assess its impact
  on utility. (3) We analyse how model types - Diffusion, VAE, and GAN - affect the
  utility-privacy trade-off. Our results show that DP-SGD significantly impacts performance,
  although some utility remains if the datasets is sufficiently large. The proposed
  DP mechanism improves training stability, particularly when combined with DP-SGD,
  for unstable models such as GANs and on smaller datasets. Diffusion models yield
  the best utility without guarantees, but with DP-SGD, GANs perform best, indicating
  that the best non-private model is not necessarily optimal when targeting formal
  guarantees. In conclusion, DP trajectory generation remains a challenging task,
  and formal guarantees are currently only feasible with large datasets and in constrained
  use cases.

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
- name: arXiv
  url: https://arxiv.org/abs/2506.09312
- name: URL
  url: https://doi.org/10.48550/ARXIV.2506.09312
---

Add the **full text** or **supplementary notes** for the publication here using Markdown formatting.
