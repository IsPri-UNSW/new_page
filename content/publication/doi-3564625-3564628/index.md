---
title: Reconstruction Attack on Differential Private Trajectory Protection Mechanisms

# Authors
# A YAML list of author names
# If you created a profile for a user (e.g. the default `admin` user at `content/authors/admin/`), 
# write the username (folder name) here, and it will be replaced with their full name and linked to their profile.
authors:
- Erik Buchholz
- Sharif Abuadbba
- Shuo Wang
- Surya Nepal
- Salil Kanhere

# Author notes (such as 'Equal Contribution')
# A YAML list of notes for each author in the above `authors` list
author_notes: []

date: '2022-12-01'

# Date to publish webpage (NOT necessarily Bibtex publication's date).
publishDate: '2025-11-11T03:05:37.343357Z'

# Publication type.
# A single CSL publication type but formatted as a YAML list (for Hugo requirements).
publication_types:
- paper-conference

# Publication name and optional abbreviated publication name.
publication: "*Proceedings of the 38th Annual Computer Security Applications Conference
  (ACSAC '22)*"
publication_short: ''

doi: 10.1145/3564625.3564628

abstract: Location trajectories collected by smartphones and other devices represent
  a valuable data source for applications such as location-based services. Likewise,
  trajectories have the potential to reveal sensitive information about individuals,
  e.g., religious beliefs or sexual orientations. Accordingly, trajectory datasets
  require appropriate sanitization.  Due to their strong theoretical privacy guarantees,
  differential private publication mechanisms receive much attention.  However, the
  large amount of noise required to achieve differential privacy yields structural
  differences, e.g., ship trajectories passing over land. We propose a deep learning-based
  Reconstruction Attack on Protected Trajectories (RAoPT), that leverages the mentioned
  differences to partly reconstruct the original trajectory from a differential private
  release. The evaluation shows that our RAoPT model can reduce the Euclidean and
  Hausdorff distances between the released and original trajectories by over 68% on
  two real-world datasets under protection with ɛ ≤ 1. In this setting, the attack
  increases the average Jaccard index of the trajectories' convex hulls, representing
  a user's activity space, by over 180%. Trained on the GeoLife dataset, the model
  still reduces the Euclidean and Hausdorff distances by over 60% for T-Drive trajectories
  protected with a state-of-the-art mechanism (ɛ = 0.1). This work highlights shortcomings
  of current trajectory publication mechanisms, and thus motivates further research
  on privacy-preserving publication schemes.

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
  url: https://arxiv.org/abs/2210.09375
- name: URL
  url: https://doi.org/10.1145/3564625.3564628
---


