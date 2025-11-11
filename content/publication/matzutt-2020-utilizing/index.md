---
title: Utilizing Public Blockchains for the Sybil-Resistant Bootstrapping of Distributed
  Anonymity Services

# Authors
# A YAML list of author names
# If you created a profile for a user (e.g. the default `admin` user at `content/authors/admin/`), 
# write the username (folder name) here, and it will be replaced with their full name and linked to their profile.
authors:
- Roman Matzutt
- Jan Pennekamp
- Erik Buchholz
- Klaus Wehrle

# Author notes (such as 'Equal Contribution')
# A YAML list of notes for each author in the above `authors` list
author_notes: []

date: '2020-10-01'

# Date to publish webpage (NOT necessarily Bibtex publication's date).
publishDate: '2025-11-11T00:08:44.641145Z'

# Publication type.
# A single CSL publication type but formatted as a YAML list (for Hugo requirements).
publication_types:
- paper-conference

# Publication name and optional abbreviated publication name.
publication: "*Proceedings of the 15th ACM ASIA Conference on Computer and Communications
  Security (ASIACCS '20)*"
publication_short: ''

doi: 10.1145/3320269.3384729

abstract: 'Distributed anonymity services, such as onion routing networks or cryptocurrency
  tumblers, promise privacy protection without trusted third parties. While the security
  of these services is often well-researched, security implications of their required
  bootstrapping processes are usually neglected: Users either jointly conduct the
  anonymization themselves or they need to rely on a set of non-colluding privacy
  peers. However, the typically small number of privacy peers enable single adversaries
  to mimic distributed services. We thus present AnonBoot, a Sybil-resistant medium
  to securely bootstrap distributed anonymity services via public blockchains. AnonBoot
  enforces that peers periodically create a small proof of work to refresh their eligibility
  of providing secure anonymity services. A pseudo-random, locally replicable bootstrapping
  process using on-chain entropy then prevents biasing the election of eligible peers.
  Our evaluation using Bitcoin as AnonBoot’s underlying blockchain shows its feasibility
  to maintain a trustworthy repository of 1000 peers with only a small storage footprint
  while supporting arbitrarily large user bases on top of most blockchains.'

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
  url: https://doi.org/10.1145/3320269.3384729
---

Add the **full text** or **supplementary notes** for the publication here using Markdown formatting.
