---
title: CV
---
<section class='block'><h2 class='block-title' id='persoonlijke-gegevens'>PERSOONLIJKE GEGEVENS</h2>
{{ render_personal_data() }}
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='kernexpertise'>KERNEXPERTISE</h2>
{{ render_expertise_tags() }}
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='persoonlijk'>PERSOONLIJK</h2>
{{ render_personal_text() }}
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='achtergrond'>ACHTERGROND</h2>
<div class="engagement-item"><div class="engagement-summary" role="button" tabindex="0" aria-expanded="false"><span class="engagement-toggle">▶</span><div class="engagement-summary-content"><span class="engagement-org">Opleidingen en belangrijkste certificeringen</span></div></div><div class="engagement-details">
<div class="engagement-detail-item"><div class="detail-label">Opleidingen</div>{{ render_education_table('educations', bold=True) }}</div>
<div class="engagement-detail-item"><div class="detail-label">Belangrijkste certificeringen</div>{{ render_education_table('certifications', bold=False) }}</div>
</div></div>
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='cursussen'>CURSUSSEN</h2>
<div class="engagement-item"><div class="engagement-summary" role="button" tabindex="0" aria-expanded="false"><span class="engagement-toggle">▶</span><div class="engagement-summary-content"><span class="engagement-org">Bekijk gevolgde cursussen</span></div></div><div class="engagement-details">
{{ render_courses('courses') }}
</div></div>
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='overige-cursussen'>OVERIGE CURSUSSEN</h2>
<div class="engagement-item"><div class="engagement-summary" role="button" tabindex="0" aria-expanded="false"><span class="engagement-toggle">▶</span><div class="engagement-summary-content"><span class="engagement-org">Bekijk overige cursussen</span></div></div><div class="engagement-details">
{{ render_courses('courses-short') }}
</div></div>
</section>
<div class='block-sep'></div>

<section class='block'><h2 class='block-title' id='werkervaring'>WERKERVARING</h2>
{{ render_engagements() }}
</section>
