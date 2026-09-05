---
layout: page
title: software
permalink: /software/
description: Here are some of my most recent open-source software.
nav: true
nav_order: 2
display_categories: [maintained, old]
horizontal: false
---

<!-- pages/software.md -->
<div class="projects">
{% if site.enable_project_categories and page.display_categories %}
  <!-- Display categorized projects -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_projects = site.projects | where: "category", category %}
  {% assign sorted_projects = categorized_projects | sort: "importance" %}
  <!-- Generate cards for each project -->
  {% if page.horizontal %}
  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

{% else %}

<!-- Display projects without categories -->

{% assign sorted_projects = site.projects | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>

## Other contributions

Over the years I contributed to a lot of open source projects, among which [pybliometrics](https://github.com/pybliometrics-dev/pybliometrics/commits/master/?author=raffaelemancuso), [pyalex](https://github.com/J535D165/pyalex/commits/main/?author=raffaelemancuso) and [modelsummary](https://github.com/vincentarelbundock/modelsummary/commits/main/?author=raffaelemancuso).

I also helped my research group [develop its website](http://www.efi.polimi.it).
