---
layout: page
permalink: /publications/
title: publications
description: scientific papers, work in progress, and policy briefs.
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

<h2>Scientific papers</h2>

<h3>Published</h3>

{% bibliography --group_by none --query @*[status=published]* %}

<h3>Under review</h3>

{% bibliography --group_by none --query @*[status=under_review]* %}

<h3>Work in progress</h3>

{% bibliography --group_by none --query @*[status=wip]* %}

<h2>Policy briefs</h2>

{% bibliography --group_by none --query @*[status=policy_brief]* %}

</div>
