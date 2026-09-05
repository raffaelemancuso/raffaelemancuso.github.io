---
layout: page
permalink: /talks/
title: talks
description: conference presentations, by year.
nav: true
nav_order: 5
---

<!-- _pages/talks.md: data in _data/talks.yml, rendered with the same look as the publications list -->

<style>
  .publications ol.bibliography ul.talk-contributions {
    margin: 0.25rem 0 0;
    padding-left: 1.25rem;
  }
  .publications ol.bibliography ul.talk-contributions li {
    margin: 0;
    padding: 0;
  }
</style>

<div class="publications">
{% assign talks_by_year = site.data.talks | group_by: "year" | sort: "name" | reverse %}
{% for year in talks_by_year %}
<h2 class="year">{{ year.name }}</h2>
<ol class="bibliography">
{% for talk in year.items %}
<li>
<div class="row">
<div class="col col-sm-2 abbr">
<abbr class="badge rounded w-100">{{ talk.abbr }}</abbr>
</div>
<div class="col col-sm-10">
<div class="title"><a href="{{ talk.url }}">{{ talk.name }}</a></div>
{% if talk.venue %}<div class="periodical">{{ talk.venue }}</div>{% endif %}
<div class="periodical">{{ talk.city }}</div>
<div class="periodical">{{ talk.dates }}</div>
<ul class="talk-contributions">
{% for item in talk.contributions %}
<li>{{ item }}</li>
{% endfor %}
</ul>
</div>
</div>
</li>
{% endfor %}
</ol>
{% endfor %}
</div>
