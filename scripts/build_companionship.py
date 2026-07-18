#!/usr/bin/env python3
"""Clone the /services/personal-care/ mirrored template and repopulate it with companionship content."""
from bs4 import BeautifulSoup
import os

MIR = '/Users/hassankhan/Documents/truehomecare/site/src/mirror/pages'
src = open(MIR + '/services__personal-care.html').read()
soup = BeautifulSoup(src, 'html.parser')

def set_text(el, text):
    el.clear(); el.append(text)

def set_html(el, html):
    el.clear()
    for node in list(BeautifulSoup(html, 'html.parser').contents):
        el.append(node)

def sel1(css):
    el = soup.select_one(css)
    assert el is not None, 'missing: ' + css
    return el

def selall(css, n=None):
    els = soup.select(css)
    if n is not None: assert len(els) >= n, f'{css}: found {len(els)} need {n}'
    return els

# ---------- HERO ----------
set_text(sel1('.tv-service-hero__title'), 'Companionship Care At Home')
set_html(sel1('.tv-service-hero__text'),
    '<p>True Homecare is a premier provider of professional companionship services. Available across '
    'Wilmslow and Stockport with deep regional expertise, our person-centred approach focuses on enhancing '
    'quality of life and emotional wellbeing, ensuring clients maintain their independence and dignity within '
    'the comfort of their own homes.</p>')
# hero image
hero_img = sel1('.tv-service-hero__image')
new_hero = '/images/2025-06-truehomecare-companionship-at-home-e1750159124947-1024x683.png'
for a in ('src', 'data-src', 'srcset', 'data-srcset'):
    if hero_img.has_attr(a): del hero_img[a]
hero_img['src'] = new_hero
hero_img['alt'] = 'Companionship Care at Home'

# ---------- CARE PROCESS (How do I arrange) ----------
set_text(sel1('.tv-care-process-section__main-heading'), 'How do I arrange Companionship?')
set_html(sel1('.tv-care-process-section__main-content'),
    "Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a "
    "safeguarding-compliant companionship package, tailored perfectly to the client's personality, social needs, "
    "and emotional wellbeing. By providing this professional service, we also offer essential respite to family "
    "members, allowing you to return to your roles as family rather than full-time caregivers, knowing your "
    "relative is socially active and happy.")
proc_head = selall('.tv-care-process-card__heading', 3)
proc_body = selall('.tv-care-process-card__content', 3)
procs = [
    ('1. Contact our Companionship Experts',
     "Get in touch with our Stockport and Wilmslow-based team at 01614281989 using our secure online enquiry form "
     "to discuss your family's specific options. Our dedicated support team is available 24/7 and aims to respond "
     "to all adult social care enquiries immediately to provide instant peace of mind. Whether you need companionship "
     "alone or in combination with our other services—such as Domiciliary Care, Stroke Care, Long-Term Condition "
     "Support, or Respite Care—we are here to help."),
    ('2. Free In-Home Assessment within 24 hours',
     "Our team comprises skilled professionals, care managers, care coordinators, and caregivers who are experts in "
     "palliative home care. They will discuss your requirements, learn more about the client's hobbies, interests, "
     "and daily routine, and carry out a free assessment in their own home. This helps us understand the exact type "
     "of emotional support required to effectively combat loneliness, whether the client would benefit from 24-hour "
     "support, waking nights, sleeping nights, or assistance with outings such as taking a walk in the park, a movie, "
     "or a hospital visit."),
    ('3. Your bespoke Companionship package',
     "Our team will create a fully person-centred care package based on exact needs and preferences. We strictly "
     "adhere to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff "
     "are carefully matched based on individual personality traits, shared interests, and specific cognitive "
     "requirements—including support for Parkinson's clients. We work alongside other healthcare professionals like "
     "district nurses, GPs, hospitals, and pharmacists to ensure that our care is consistent, compassionate, and "
     "supportive of both the client and their family."),
]
for i, (h, b) in enumerate(procs):
    set_text(proc_head[i], h)
    set_html(proc_body[i], f'<p>{b}</p>')

# ---------- EXPERTS SECTION ----------
set_text(sel1('.experts-content h2'), 'Combatting Loneliness with Expert Emotional Support')
set_html(sel1('.experts-text'),
    "<p>Social isolation can significantly impact a client's mental and physical health, often becoming a primary "
    "challenge for concerned family members. True Homecare addresses this by providing consistent, meaningful human "
    "connection that brings immediate emotional relief to both clients and their relatives. Our team comprises "
    "skilled professionals, care managers, care coordinators, and caregivers who are experts in palliative home care. "
    "They offer emotional stability and mental stimulation to reduce anxiety, ensuring the client feels valued while "
    "meeting the highest standards of our Care Quality Commission (CQC) rated ‘Good’ home care services. By providing "
    "this professional support, we offer essential respite to family members, allowing you to return to your roles as "
    "family rather than full-time caregivers, knowing your relative is in safe hands.</p>")

# ---------- FEATURE INTRO ----------
set_text(sel1('.feature-intro-heading'), 'Expert Care, Real Results: How We Support Independence')
set_html(sel1('.feature-intro-content'),
    "<p>True Homecare's professional companionship services provide the profound peace of mind that comes from "
    "knowing your relative is socially engaged, emotionally valued, and never lonely within their own home. By "
    "transitioning from the stress of social isolation to our personalised, dedicated companionship, our clients "
    "experience a measurable improvement in their daily quality of life, mental stimulation, and emotional wellbeing.</p>")
# (keep the 3 generic value cards as-is — they are brand-universal)

# ---------- BENEFITS (6 features) ----------
set_text(sel1('.benefits-main-heading'), 'Our Comprehensive Companionship Support Features')
ben_head = selall('.benefit-card-heading', 6)
ben_body = selall('.benefit-card-content', 6)
benefits = [
    ('Social Engagement & Befriending',
     "Our companions provide meaningful conversation and engage in shared hobbies, ensuring our clients remain socially "
     "active and emotionally connected through genuine, trusted human interaction and dedicated befriending. By "
     "providing this consistent support, we also offer essential respite and emotional relief to family members, "
     "ensuring you can return to your roles as family rather than full-time caregivers."),
    ('Community Access & Outings',
     "We provide safe accompaniment to medical appointments, social clubs, and local events, helping clients maintain "
     "their community ties and navigate the outside world confidently with a trained care professional. Whether it is "
     "a walk in the park, a movie, or a hospital visit, we ensure the client feels secure and supported."),
    ('Mental & Cognitive Stimulation',
     "To support mental health and cognitive wellbeing, our team engages clients in puzzles, reading, and memory games, "
     "providing the mental exercise necessary to keep the mind sharp. Our team comprises skilled professionals, care "
     "managers, care coordinators, and caregivers who are experts in palliative home care, ensuring this stimulation is "
     "delivered with clinical professionalism."),
    ('Light Household Help & Errands',
     "We assist with light housekeeping and meal preparation, reducing the stress of daily chores so the client can "
     "focus on enjoying their time and improving their overall wellbeing."),
    ('Digital Connectivity & Tech Support',
     "Our team helps clients stay connected by assisting with video calls to family members and managing digital "
     "correspondence. We bridge the gap between traditional living and modern technology with patient training and guidance."),
    ('Routine Wellness Checks & Safety',
     "We provide consistent monitoring of emotional states and physical safety, offering peace of mind to the client and "
     "their family. We liaise with GPs, pharmacists, and district nurses to identify changes in wellbeing and ensure a "
     "secure, hazard-free home environment every single day. We strictly adhere to the Ethical Framework by Stockport "
     "Council in all our operations."),
]
for i, (h, b) in enumerate(benefits):
    set_text(ben_head[i], h)
    set_html(ben_body[i], f'<p>{b}</p>')

# ---------- PHONE CTA ----------
set_text(sel1('.phone-cta-text'), 'Call us to find out more about Companionship')

# ---------- WHY CHOOSE (two sections) ----------
why_secs = selall('.why-choose-section', 2)
set_text(why_secs[0].select_one('.why-choose-content h2'), 'Why True Homecare is the Leading Choice')
set_html(why_secs[0].select_one('.why-choose-text'),
    "<p>True Homecare delivers CQC-rated, personalised companionship rooted in dignity, respect, and genuine social "
    "connection. Our team comprises skilled professionals, care managers, care coordinators, and caregivers who are "
    "experts in palliative home care. Beyond our experience, we strictly adhere to the Ethical Framework by Stockport "
    "Council, working in seamless collaboration with healthcare professionals like district nurses, GPs, and pharmacists. "
    "We provide the tailored, high-quality emotional support every client deserves to remain socially active and engaged "
    "in the comfort of their own home.</p>")
set_text(why_secs[1].select_one('.why-choose-content h2'), 'Delivering Excellence in Private Companionship')
set_html(why_secs[1].select_one('.why-choose-text'),
    "<p>We are deeply committed to delivering compassionate, high-quality companionship and social support. True "
    "Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The happiness, social "
    "engagement, and emotional wellbeing of our clients are our absolute top priorities. We strive for regulated "
    "excellence in everything we do—whether providing 24-hour support, waking nights, or assisting with outings like "
    "walks in the park—to ensure every client and their family member receives the emotional support and respite they "
    "deserve.</p>")

# ---------- CARE OPTIONS (Integrated Social Care Solutions) ----------
set_text(sel1('.care-options-header h2'), 'Integrated Social Care Solutions')
set_html(sel1('.care-options-header div'),
    "<p>We seamlessly blend companionship with wider home care options, ensuring a holistic approach for our clients. "
    "Explore our CQC-rated Alzheimer and Dementia Care and 24-hour support for a fully integrated care plan that "
    "supports the entire family.</p>")
cards = selall('.care-option-card', 2)
care_cards = [
    {
        'img': '/images/2025-06-live-in-care-services-truehomecare-e1750160172719.webp',
        'alt': '24-Hour Live-in Care',
        'title': '24-Hour Live-in Care',
        'body': "Avoid the stress of moving to a residential facility. Our premium live-in care provides 24-hour support "
                "from a dedicated professional. Experience true one-to-one assistance that guarantees safety, dignity, and "
                "complete peace of mind in your own home, while providing family members with essential respite.",
        'items': [
            ('Expert, Handpicked Carers', "We never do random placements. Every carer is rigorously vetted, undergoes "
             "comprehensive training, and is carefully matched to the client's personality, hobbies, and values."),
            ('Complex Needs & Conditions', "Our team comprises skilled professionals, care managers, care coordinators, and "
             "caregivers who are experts in palliative home care. We manage advanced requirements safely at home, including "
             "support for Parkinson's clients, Stroke Care, and palliative care."),
            ('Total Peace of Mind for Families', "Relieve the pressure on family members. Rest easy knowing the client is "
             "receiving continuous, compassionate supervision and immediate support, including waking nights or sleeping "
             "nights if required."),
        ],
        'btn': ('Explore Live-in Care', '/services/live-in-care/'),
    },
    {
        'img': None,  # keep template image (dementia) — good match
        'alt': 'Alzheimer and Dementia Care',
        'title': 'Alzheimer and Dementia Care',
        'body': "Keep the client safe in their most familiar surroundings. Our bespoke dementia support provides expert, "
                "CQC-rated assistance tailored to your exact schedule. We actively manage the complexities of memory-related "
                "health conditions so the client can maintain their routine securely and happily at home.",
        'items': [
            ('Consistent, Familiar Routine', "Routine is critical. Our dedicated team structures support around the client's "
             "existing habits to minimise confusion, reduce anxiety, and create a calm environment."),
            ('Specialist Memory Support', "For Dementia, one caregiver serves the client; because if there is a new carer, "
             "they cannot monitor and diagnose a client's health condition with consistency. We expertly manage symptoms and "
             "ensure medications are taken safely in liaison with GPs and pharmacists."),
            ('Essential Respite for Families', "Caring for a relative with memory loss is emotionally exhausting. Our flexible "
             "respite care gives family members crucial time to rest and recharge with complete peace of mind, knowing the "
             "client is in safe, professional hands."),
        ],
        'btn': ('Request Dementia Assessment', '/services/dementia-and-alzheimer-care/'),
    },
]
for ci, card in enumerate(cards):
    data = care_cards[ci]
    if data['img']:
        im = card.select_one('.care-option-image img')
        for a in ('src', 'data-src', 'srcset', 'data-srcset'):
            if im.has_attr(a): del im[a]
        im['src'] = data['img']; im['alt'] = data['alt']
    set_text(card.select_one('h3'), data['title'])
    set_html(card.select_one('.care-option-content'), f"<p>{data['body']}</p>")
    items = card.select('.care-item')
    for ii, (q, a) in enumerate(data['items']):
        btn = items[ii].select_one('.care-question')
        # rebuild question button preserving tick + arrow spans
        btn.clear()
        tick = soup.new_tag('span'); tick['class'] = 'tick'; tick.string = '✓'
        arrow = soup.new_tag('span'); arrow['class'] = 'arrow'; arrow.string = '+'
        btn.append(tick); btn.append(' ' + q + ' '); btn.append(arrow)
        set_text(items[ii].select_one('.care-answer'), ' ' + a)
    a_btn = card.select_one('.care-btn')
    set_text(a_btn, data['btn'][0]); a_btn['href'] = data['btn'][1]

# ---------- CONTENT SECTION (Authority + comparison table) ----------
comparison_rows = [
    ('Retain independence in a familiar, comfortable environment', '✅', '❌'),
    ('Dedicated one-to-one matched carer relationship', '✅', '❌'),
    ('Ability to keep existing pets and maintain lifelong daily routines', '✅', '❌'),
    ('Complete flexibility over meal choices and family visiting hours', '✅', '❌'),
    ('Cost-effective scaling based purely on the exact hours of support needed', '✅', '❌'),
]
rows_html = (
    '<tr><td><p><strong>Care Criteria &amp; Benefits</strong></p></td>'
    '<td><p><strong>True Homecare</strong></p></td><td><p><strong>Residential Care</strong></p></td></tr>'
)
for crit, a, b in comparison_rows:
    rows_html += f'<tr><td><p><strong>{crit}</strong></p></td><td><p>{a}</p></td><td><p>{b}</p></td></tr>'

content_html = (
    '<h3><strong>The True Homecare Standard: Authority &amp; Core Values</strong></h3>'
    '<h4><strong>The Matching Process</strong></h4>'
    '<p>We do not believe in random assignments. Our team conducts a detailed personality assessment to pair clients '
    'with caregivers who share similar interests, hobbies, and values, ensuring a natural friendship develops from the '
    'first visit. This approach not only supports the client but provides essential emotional relief and respite for '
    'family members.</p>'
    '<h4><strong>Step-by-Step Care Planning</strong></h4>'
    '<p>We build a bespoke framework for the client’s daily life, strictly adhering to the Ethical Framework by Stockport '
    'Council:</p><ul>'
    '<li><strong>Step 1:</strong> Initial In-Home Assessment to gauge mobility, health conditions, and social needs.</li>'
    '<li><strong>Step 2:</strong> Matching with a fully-vetted local care professional from our team of skilled '
    'professionals, care managers, care coordinators, and caregivers who are experts in palliative home care.</li>'
    '<li><strong>Step 3:</strong> Creation of a personalised social calendar mapping out activities and visits—such as '
    'walks in the park, movies, or hospital visits.</li>'
    '<li><strong>Step 4:</strong> Ongoing reviews to adapt the care plan as the client’s needs evolve, in liaison with '
    'GPs, pharmacists, and district nurses.</li></ul>'
    '<h4><strong>Skilled and Certified Caregivers</strong></h4>'
    '<p>Quality is maintained through rigorous staff vetting. Every companion undergoes comprehensive background checks, '
    'safeguarding protocols, and specialised training to ensure they meet our professional standards for safety, ethics, '
    'and care, aligned with UK healthcare regulations. Please note that for Dementia, one caregiver serves the client; '
    'because if there is a new carer, they cannot monitor and diagnose a client’s health condition with consistency.</p>'
    '<h4><strong>Mental Health Focus</strong></h4>'
    '<p>Consistent companionship is a vital tool in maintaining cognitive health. By providing regular social interaction '
    'and mental stimulation, we help reduce the risk of cognitive decline and protect against the severe health effects of '
    'social isolation. We also provide specialist support for Parkinson’s clients and those requiring palliative care, '
    'ensuring the client feels valued and supported while their family receives the respite they need.</p>'
    '<h2><strong>Companionship Care vs. Residential Facilities</strong></h2>'
    '<p>Understanding your options is critical. While care homes offer structured environments, our private companionship '
    'services empower seniors to remain happily and safely in their own beloved homes.</p>'
    f'<table><tbody>{rows_html}</tbody></table>'
)
set_html(sel1('.content-section-text'), content_html)

# ---------- FAQ ----------
set_text(sel1('.faq-heading'), 'Companionship Care FAQs')
faq_items = selall('.faq-item', 5)
faqs = [
    ('What exactly are companionship services?',
     "Companionship services provide non-medical emotional and social support. This includes activities like conversation, "
     "accompanying your loved one to appointments, and helping with light household tasks to prevent isolation and improve "
     "overall wellbeing."),
    ("How do you match a carer to my relative's specific hobbies in Stockport or Wilmslow?",
     "We conduct an initial assessment to understand your relative's interests and personality. We then pair them with a "
     "professional companion from your local area who shares similar passions, ensuring a natural connection and genuine friendship."),
    ('Is companionship care available in my specific UK city?',
     "Yes, True Homecare operates across the UK. Please contact our regional coordinators to confirm availability and local "
     "capacity in your specific city or town."),
    ('What is the difference between companion care and personal care?',
     "Companion care focuses on emotional support and social engagement. Personal care involves hands-on physical assistance, "
     "such as bathing, dressing, and medication management."),
    ('How quickly can companionship services begin?',
     "Services can often begin shortly after an initial assessment and care plan creation. Contact us today to determine the "
     "fastest start date for your location."),
]
for i, (q, a) in enumerate(faqs):
    set_text(faq_items[i].select_one('.faq-question span:first-child'), q)
    set_html(faq_items[i].select_one('.faq-answer'), f'<p>{a}</p>')

out = MIR + '/services__companionship.html'
open(out, 'w').write(str(soup))
print('WROTE', out, len(str(soup)), 'bytes')
print('sections OK: hero, care-process(3), experts, feature-intro, benefits(6), phone-cta, why-choose(2), care-options(2), content, faq(5)')
