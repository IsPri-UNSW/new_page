---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        Welcome to the **IsPri UNSW** Research Group
      image:
        filename: 'carousel/team_0.jpg'
      text: |
        <br>
        
        The Information Security and Privacy Research Group’s mission is to conduct advanced applied security research and devise practical solutions to address real-world information security and privacy challenges.

  - block: markdown
    content:
      title: Description
      subtitle: ''
      text: |
        The group’s members have an established track record of conducting research with impact and have secured major national and international research grants from both government and industry. Areas include: security of critical infrastructure; secure software systems and communication protocols; secure authentication and identity management; security of AI algorithms and systems; security and privacy by design solutions; security and privacy of social systems, and blockchain security and privacy.
    design:
      columns: '1'
      # background:
      # spacing:
      #   padding: ['20px', '0', '20px', '0']
      # css_class: fullscreen
  
  - block: collection
    content:
      title: Latest News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '1'
  
  - block: markdown
    content:
      title:
      subtitle: ''
      text:
    design:
      columns: '1'
      background:
        image: 
          filename: 'carousel/team_1.jpg'
          filters:
            brightness: 1
          parallax: false
          position: center
          size: cover
          text_color_light: true
      spacing:
        padding: ['20px', '0', '20px', '0']
      css_class: fullscreen

  - block: collection
    content:
      title: Latest Publications
      text: ""
      count: 5
      filters:
        folders:
          - publication
        publication_type: 'article'
    design:
      view: citation
      columns: '1'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'
---
