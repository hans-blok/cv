---
title: CV
---
<section class='block'><div class='block-title'>PERSOONLIJKE GEGEVENS</div>
{{ render_personal_data() }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>WERKERVARING</div>
{{ render_engagements() }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>PERSOONLIJK</div>
{{ render_personal_text() }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>OPLEIDINGEN</div>
{{ render_education_table('educations', bold=True) }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>BELANGRIJKSTE CERTIFICERINGEN</div>
{{ render_education_table('certifications', bold=False) }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>CURSUSSEN</div>
{{ render_courses('courses') }}
</section>
<div class='block-sep'></div>

<section class='block'><div class='block-title'>OVERIGE CURSUSSEN</div>
{{ render_courses('courses-short') }}
</section>
