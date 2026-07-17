#!/usr/bin/env python3
"""Generate service pages from the /services/personal-care/ mirrored template + structured content."""
from bs4 import BeautifulSoup
import json, os

MIR = '/Users/hassankhan/Developer/THC/site/src/mirror/pages'
TEMPLATE = open(MIR + '/services__personal-care.html').read()
MANIFEST = '/Users/hassankhan/Developer/THC/site/src/data/mirror-manifest.json'

def paras(*ps):
    return ''.join(f'<p>{p}</p>' for p in ps)

def table_html(rows, header=('Care Criteria & Benefits', 'True Homecare', 'Residential Care')):
    h = f'<tr><td><p><strong>{header[0]}</strong></p></td><td><p><strong>{header[1]}</strong></p></td><td><p><strong>{header[2]}</strong></p></td></tr>'
    for crit in rows:
        h += f'<tr><td><p><strong>{crit}</strong></p></td><td><p>✅</p></td><td><p>❌</p></td></tr>'
    return f'<table><tbody>{h}</tbody></table>'

def build(cfg):
    soup = BeautifulSoup(TEMPLATE, 'html.parser')

    def set_text(el, t): el.clear(); el.append(t)
    def set_html(el, html):
        el.clear()
        for n in list(BeautifulSoup(html, 'html.parser').contents): el.append(n)
    def one(css):
        e = soup.select_one(css); assert e, 'missing ' + css; return e
    def many(css, n):
        e = soup.select(css); assert len(e) >= n, f'{css} {len(e)}<{n}'; return e

    # HERO
    set_text(one('.tv-service-hero__title'), cfg['hero_title'])
    set_html(one('.tv-service-hero__text'), f"<p>{cfg['hero_text']}</p>")
    hi = one('.tv-service-hero__image')
    for a in ('src', 'data-src', 'srcset', 'data-srcset'):
        if hi.has_attr(a): del hi[a]
    hi['src'] = cfg['hero_img']; hi['alt'] = cfg['hero_title']

    # CARE PROCESS
    set_text(one('.tv-care-process-section__main-heading'), cfg['process_heading'])
    set_html(one('.tv-care-process-section__main-content'), cfg['process_intro'])
    ph = many('.tv-care-process-card__heading', 3); pb = many('.tv-care-process-card__content', 3)
    for i, (h, b) in enumerate(cfg['process_cards']):
        set_text(ph[i], h); set_html(pb[i], f'<p>{b}</p>')

    # EXPERTS
    set_text(one('.experts-content h2'), cfg['experts_heading'])
    set_html(one('.experts-text'), paras(*cfg['experts_paras']))

    # FEATURE INTRO (keep the 3 generic value cards)
    set_text(one('.feature-intro-heading'), cfg['feature_heading'])
    set_html(one('.feature-intro-content'), f"<p>{cfg['feature_text']}</p>")

    # BENEFITS (6)
    set_text(one('.benefits-main-heading'), cfg['benefits_heading'])
    bh = many('.benefit-card-heading', 6); bb = many('.benefit-card-content', 6)
    for i, (h, b) in enumerate(cfg['benefits']):
        set_text(bh[i], h); set_html(bb[i], f'<p>{b}</p>')

    # PHONE CTA
    set_text(one('.phone-cta-text'), cfg['phone_cta'])

    # WHY CHOOSE (2)
    wc = many('.why-choose-section', 2)
    set_text(wc[0].select_one('.why-choose-content h2'), cfg['why1'][0])
    set_html(wc[0].select_one('.why-choose-text'), f"<p>{cfg['why1'][1]}</p>")
    set_text(wc[1].select_one('.why-choose-content h2'), cfg['why2'][0])
    set_html(wc[1].select_one('.why-choose-text'), f"<p>{cfg['why2'][1]}</p>")

    # CARE OPTIONS (2 cards, 3 accordions each)
    set_text(one('.care-options-header h2'), cfg['careopts_heading'])
    set_html(one('.care-options-header div'), f"<p>{cfg['careopts_intro']}</p>")
    cards = many('.care-option-card', 2)
    for ci, card in enumerate(cards):
        c = cfg['careopts_cards'][ci]
        if c.get('img'):
            im = card.select_one('.care-option-image img')
            for a in ('src', 'data-src', 'srcset', 'data-srcset'):
                if im.has_attr(a): del im[a]
            im['src'] = c['img']; im['alt'] = c['title']
        set_text(card.select_one('h3'), c['title'])
        set_html(card.select_one('.care-option-content'), f"<p>{c['body']}</p>")
        items = card.select('.care-item')
        for ii, (q, a) in enumerate(c['items']):
            btn = items[ii].select_one('.care-question'); btn.clear()
            tick = soup.new_tag('span'); tick['class'] = 'tick'; tick.string = '✓'
            arrow = soup.new_tag('span'); arrow['class'] = 'arrow'; arrow.string = '+'
            btn.append(tick); btn.append(' ' + q + ' '); btn.append(arrow)
            set_text(items[ii].select_one('.care-answer'), ' ' + a)
        b = card.select_one('.care-btn'); set_text(b, c['btn'][0]); b['href'] = c['btn'][1]

    # CONTENT SECTION
    set_html(one('.content-section-text'), cfg['content_html'])

    # FAQ (variable count; trim any leftover template items)
    set_text(one('.faq-heading'), cfg['faq_heading'])
    fi = many('.faq-item', len(cfg['faqs']))
    for i, (q, a) in enumerate(cfg['faqs']):
        set_text(fi[i].select_one('.faq-question span:first-child'), q)
        set_html(fi[i].select_one('.faq-answer'), f'<p>{a}</p>')
    for extra in fi[len(cfg['faqs']):]:
        extra.decompose()

    open(MIR + '/' + cfg['file'], 'w').write(str(soup))
    return cfg['file']

# ============ IMAGES ============
IMG_COMP = '/wp-content/uploads/2025/06/truehomecare-companionship-at-home-e1750159124947-1024x683.png'
IMG_LIVEIN = '/wp-content/uploads/2025/06/live-in-care-services-truehomecare-e1750160172719.webp'
IMG_DEM = '/wp-content/uploads/2026/01/Treatment-for-Lewy-Body-dementia-UK.jpg'
IMG_RESP = '/wp-content/uploads/2025/10/Taking-Care-of-the-Carer_-Respite-and-Family-Support.jpg'

TEAM = "Our team comprises skilled professionals, care managers, care coordinators, and caregivers who are experts in palliative home care."

# ============ LIVE-IN CARE ============
livein = {
 'file': 'services__live-in-care.html', 'route': '/services/live-in-care/',
 'm_title': '24-Hour Live-in Care in Stockport & Wilmslow | True Homecare',
 'm_desc': 'Premium private 24-hour live-in care across Stockport, Wilmslow & Cheshire. One-to-one CQC-rated support that keeps loved ones safe and independent at home. Call 0161 428 1989.',
 'hero_title': '24 Hour Live-in Care', 'hero_img': IMG_LIVEIN,
 'hero_text': "True Homecare provides premium private live-in care designed to help individuals safely maintain their independence in the comfort of their own home. Offering person-centred professional support, we provide specialised local expertise across Wilmslow and Stockport, ensuring our clients receive high-quality, one-to-one care. By providing this professional support, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 'process_heading': 'How do I arrange 24-Hour Live-in Care?',
 'process_intro': 'Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a safeguarding-compliant live-in care package, tailored perfectly to the clinical and personal needs of our clients.',
 'process_cards': [
   ('1. Contact our Live-in Care Experts', "Get in touch with our Stockport and Wilmslow-based team at 01614281989 using our secure online enquiry form to discuss your family's specific options. Our dedicated support team is available 24/7 and aims to respond to all adult social care enquiries immediately to provide instant peace of mind. Whether you need live-in care or a combination of our other services—such as Companionship, Domiciliary Care, Stroke Care, or Long-Term Condition Support—we are here to help."),
   ('2. Free In-Home Assessment within 24 hours', f"{TEAM} They will discuss your requirements, learn more about the client's health conditions, mental health, and daily routine, and carry out a free assessment in their own home. This helps us understand the exact level of 24-hour support required, including waking nights or sleeping nights, to ensure complete safety."),
   ('3. Your bespoke Live-in Care package', "Our team will create a fully person-centred care package based on exact needs and preferences. We strictly adhere to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff are carefully matched based on individual complex care needs—including support for Parkinson's clients—shared interests, and specific cognitive requirements. We work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure that our care is consistent, compassionate, and supportive of both the client and their family."),
 ],
 'experts_heading': 'See What Our Experts Can Do',
 'experts_paras': [
   "True Homecare's 24-hour live-in care provides the profound peace of mind that comes from knowing the client is safe, dignified, and supported within their own home. By transitioning from the stress of clinical environments to our personalised, round-the-clock professional support, our clients experience a measurable improvement in their daily quality of life, comfort, and emotional wellbeing.",
   f"{TEAM} They work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure every individual receives the tailored, consistent attention they need to thrive independently. Whether this involves managing Parkinson's-related mobility needs, palliative care, or providing companionship while taking a client for a walk in the park, a movie, or a hospital visit, we are here to support your entire family.",
 ],
 'feature_heading': 'Live-in Care Your Family Can Trust',
 'feature_text': "Balancing professional responsibilities with the care of a family member often leads to significant caregiver stress and burden. True Homecare alleviates this emotional pressure, providing the ultimate relief of knowing the client is safe, dignified, and well-supported with 24-hour support, including waking nights or sleeping nights if required. Our absolute commitment to quality is backed by our Care Quality Commission (CQC) rated ‘Good’ standard, ensuring your family receives highly reliable, safeguarding-compliant care you can inherently trust.",
 'benefits_heading': 'Comprehensive Home Care Support Features',
 'benefits': [
   ('Personal Care and Daily Assistance', "Our caregivers provide dignified, person-centred support with essential daily routines, including washing, dressing, and grooming, ensuring the client feels refreshed and confident every morning. By providing this professional support, we also offer essential respite to family members, allowing you to return to your roles as family rather than full-time caregivers."),
   ('Safe Medication Management', "We ensure strict health stability through the safe administration of prescriptions and precise tracking of medications to prevent errors and maintain adherence to clinical medical plans. We liaise with GPs, pharmacists, and district nurses to ensure all medication management is consistent and safe."),
   ('Nutritional Support and Meal Planning', "Our team provides tailored meal preparation and nutritional oversight, featuring bespoke menus designed to meet complex dietary requirements and health goals while promoting wellbeing. For information regarding diabetes, we refer to the advice and resources provided by Diabetes UK."),
   ('Specialist Alzheimer and Dementia Care', "Our dedicated team provides specialist safety measures and engaging cognitive activities designed to reduce anxiety and manage symptoms. Please note that for Dementia, one caregiver serves the client; because if there is a new carer, they cannot monitor and diagnose a client's health condition with consistency."),
   ('Companionship and Social Engagement', "We actively combat loneliness by providing consistent emotional support and facilitating local community outings, such as walks in the park, visits to movies, or hospital visits. This ensures clients stay socially active and mentally stimulated, while providing family members with the emotional support they deserve."),
   ('Household Management and Light Maintenance', "To maintain a stress-free home environment, we assist with essential local shopping, running errands, and light cleaning, ensuring a safe, tidy, and organised space. We strictly adhere to the Ethical Framework by Stockport Council in all our operations."),
 ],
 'phone_cta': 'Call us to find out more about Live-in Care',
 'why1': ('Why True Homecare is the First Choice for Live-in Care', f"True Homecare delivers CQC-rated, personalised 24-hour support and live-in care rooted in dignity, respect, and clinical professionalism. {TEAM} Beyond our years of experience, we strictly adhere to the Ethical Framework by Stockport Council, working in seamless collaboration with other healthcare professionals like district nurses, GPs, hospitals, and pharmacists."),
 'why2': ('Delivering Perfection in 24-Hour Live-in Care', "We are deeply committed to delivering compassionate, high-quality 24-hour support, including waking nights and sleeping nights. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The safety, dignity, and wellbeing of our clients are our absolute top priorities. We strive for regulated excellence in everything we do, every single day."),
 'careopts_heading': 'Complementary Care Solutions',
 'careopts_intro': 'Beyond 24-hour support, we offer highly flexible alternatives tailored to your evolving needs. Explore our CQC-rated Respite Care and Dementia specialist home care.',
 'careopts_cards': [
   {'img': IMG_DEM, 'title': 'Alzheimer and Dementia Care',
    'body': "Keep the client safe in their most familiar surroundings. Our bespoke dementia support provides expert, CQC-rated assistance tailored to your exact schedule. We actively manage the complexities of memory-related health conditions so the client can maintain their routine securely and happily at home, while providing essential respite and emotional support for family members.",
    'items': [
      ('Consistent, Familiar Routine', "Routine is critical. Our dedicated team structures support around the client's existing habits to minimise confusion, reduce anxiety, and create a calm environment."),
      ('Specialist Memory Support', "For Dementia, one caregiver serves the client; because if there is a new carer, they cannot monitor and diagnose a client's health condition with consistency. Our staff undergo rigorous training to manage symptoms and ensure all medications are taken safely in liaison with GPs and pharmacists."),
      ('Essential Respite for Families', "Caring for a relative with memory loss is emotionally and physically exhausting. Our flexible care gives family members crucial time to rest and recharge with complete peace of mind, knowing the client is in safe, professional hands."),
    ], 'btn': ('Request Dementia Assessment', '/services/dementia-and-alzheimer-care/')},
   {'img': IMG_RESP, 'title': 'Private Respite Care at Home',
    'body': "Need a temporary break from caregiving? Our private, CQC-rated respite care at home provides short-term, professional relief. We step in seamlessly to ensure the client remains safe and comfortable, allowing family members to rest, recharge, or handle personal commitments—such as taking a walk in the park or visiting a movie—with complete peace of mind.",
    'items': [
      ('Seamless Routine Transition', "We mirror your exact caregiving routine. From medication schedules to preferred meal times, our professional team ensures a flawless handover so the client feels secure and undisturbed."),
      ('Highly Flexible Short-Term Cover', f"Whether you need a few hours a week, emergency overnight support, or full live-in cover for a holiday, our bespoke packages adapt to your exact schedule. {TEAM}"),
      ('Total Peace of Mind for Families', "Step away knowing your relative is supported by rigorously vetted, clinically trained experts. We actively manage all personal care and companionship, giving you the true emotional and physical break you deserve. We strictly adhere to the Ethical Framework by Stockport Council."),
    ], 'btn': ('Book Respite Cover', '/services/respite-care/')},
 ],
 'content_html': (
   '<h3><strong>The Personalised Carer Matching Process</strong></h3>'
   '<p>We believe a successful care relationship relies on deep compatibility. Our rigorous matching process goes far beyond basic clinical needs, pairing local caregivers with clients based on personality traits, shared interests, and specific complex care skill sets to ensure a harmonious living environment and a highly trusting bond. This approach not only supports the client but provides essential emotional relief and respite for family members, ensuring you can return to your roles as family rather than full-time caregivers.</p>'
   '<h3><strong>Developing a Bespoke Care Roadmap</strong></h3>'
   '<p>Every client follows a specifically tailored journey to ensure their exact medical and emotional needs are met with precision. Our step-by-step care planning process includes:</p>'
   '<ul><li><strong>Step 1 — Initial In-Home Assessment:</strong> Evaluating physical, emotional, and social requirements, often coordinating with local healthcare professionals.</li>'
   '<li><strong>Step 2 — Goal Setting:</strong> Defining key health, mobility, and lifestyle objectives.</li>'
   '<li><strong>Step 3 — Care Integration:</strong> Implementing a seamless daily schedule that fully respects the client\'s existing routines and lifelong habits, including waking nights or sleeping nights.</li>'
   '<li><strong>Step 4 — Regular Reviews:</strong> Adjusting the care roadmap collaboratively as health needs naturally evolve over time, in liaison with GPs, pharmacists, and district nurses.</li></ul>'
   '<h3><strong>Upholding CQC Standards in Daily Practice</strong></h3>'
   '<p>Quality and safety are integrated into every single shift. We strictly apply CQC regulatory standards and adhere to the Ethical Framework by Stockport Council through rigorous internal auditing, transparent reporting to family members, and continuous monitoring of care delivery. We ensure that safety, dignity, and safeguarding remain the absolute priority in every home we serve.</p>'
   f'<h3><strong>Specialist Training and Staff Qualifications</strong></h3><p>{TEAM} Our caregivers undergo continuous professional development to confidently handle highly complex health conditions at home. This includes mandatory specialist training in Alzheimer and Dementia Care—where one caregiver serves the client to ensure consistency—as well as advanced certifications in palliative care and End-of-Life Care, ensuring expert clinical oversight and deeply compassionate support.</p>'
   '<h3><strong>Choosing the Right Care Environment: Live-in Care vs Residential Care</strong></h3>'
   '<p>Deciding between home-based support and a facility is a significant choice. We strongly believe preserving personal independence at home maximises the client\'s overall emotional and physical wellbeing, while ensuring they can still enjoy outings like walks in the park, movies, or hospital visits with the support they need. Need to arrange care? Contact True Homecare today at 01614281989.</p>'
   '<h2><strong>Live-in Care vs. Residential Care</strong></h2>'
   + table_html([
     'Maintain independence and preserve identity in entirely familiar surroundings',
     'Receive highly personalized, dedicated one-to-one attention from a matched carer',
     'Experience the consistency of a dedicated professional fostering strong emotional bonds',
     'Maintaining social ties at home',
     'Benefit from a highly cost-effective care solution, particularly economical for couples',
   ])
 ),
 'faq_heading': 'Frequently Asked Questions About Live-in Care',
 'faqs': [
   ('What is live-in care and how does it differ from visiting care?', "Live-in care provides a caregiver who resides in the home, offering a continuous 24-hour support presence. Unlike domiciliary care, which consists of scheduled appointments for specific tasks, live-in care ensures constant support, companionship, and security for the client, while providing family members with the essential respite and peace of mind they deserve."),
   ('When is it time to consider live-in care?', "Consider live-in care when a client experiences increased confusion, wandering, or difficulty managing daily safety alone. These signs indicate a need for specialist, round-the-clock support. We also support Parkinson's clients and those needing palliative care to help them remain safely in their own home rather than moving to a residential setting."),
   ('How do you ensure the caregiver is a good match for the client?', f"We use strict matching criteria, pairing caregivers—from our {TEAM[7:]}—based on professional qualifications, personality traits, and shared interests to ensure emotional compatibility and a trusting relationship."),
   ('What is the role of the Care Manager in overseeing live-in care?', "Your assigned Care Manager acts as the bridge between your family and the care team. They are responsible for regular site visits, auditing care delivery against CQC standards, and strictly adhering to the Ethical Framework by Stockport Council. They work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure medication adherence and provide transparent, real-time reporting on the client's wellbeing."),
   ("What happens if the client's care needs suddenly increase?", "True Homecare's live-in packages are highly scalable. Because our Care Managers conduct regular, proactive reviews of the care plan, we can quickly increase the level of support—such as adding waking nights, sleeping nights, or specialist clinical oversight—without the trauma of moving the client to a residential setting."),
 ],
}

# ============ LONG-TERM CONDITION SUPPORT ============
longterm = {
 'file': 'services__long-term-condition-support.html', 'route': '/services/long-term-condition-support/',
 'm_title': 'Long-Term Condition Support at Home | True Homecare',
 'm_desc': 'Expert, CQC-rated long-term condition support at home across Stockport, Wilmslow & Cheshire. Clinical care for Parkinson\'s, stroke recovery & chronic conditions. Call 0161 428 1989.',
 'hero_title': 'Long-Term Care at Home', 'hero_img': '/wp-content/uploads/2025/06/Long-Term-Condition-Support-uk-truehomecare-e1750672890434.webp',
 'hero_text': "True Homecare provides expert, bespoke long-term condition support for residents across Stockport, Wilmslow, and the wider Cheshire region. Our CQC-rated care professionals deliver high-quality, clinical support in the comfort of your own home, ensuring your loved one maintains independence, safety, and dignity while effectively managing complex, ongoing health requirements through our locally-trusted expertise.",
 'process_heading': 'How do I arrange Long-Term Care at Home?',
 'process_intro': 'Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a safeguarding-compliant Long-Term Condition Support package, tailored perfectly to the clinical and personal needs of the client. By providing this professional service, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers, knowing your relative is in professional hands.',
 'process_cards': [
   ('1. Contact our Long-Term Care Experts', "Get in touch with our Stockport and Wilmslow-based team at 01614281989 using our secure online enquiry form to discuss your family's specific options. Our dedicated support team is available 24/7 and aims to respond to all adult social care enquiries immediately to provide instant peace of mind. Whether you need Long-Term Condition Support or a combination of our other services—such as Companionship, Domiciliary Care, Stroke Care, or Respite Care—we are here to help."),
   ('2. Free In-Home Assessment within 24 hours', f"{TEAM} They will discuss your requirements, learn more about the client's health history, mental health, and daily routine, and carry out a free assessment in their own home. This helps us understand the exact level of 24-hour support required, including waking nights or sleeping nights, to ensure safety and independence."),
   ('3. Your bespoke Long-Term Care package', "Our team will create a fully person-centred care package based on exact clinical needs and preferences. We strictly adhere to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff are carefully matched based on individual complex care needs—including support for Parkinson's clients—shared interests, and specific cognitive requirements. We work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure that our care is consistent, compassionate, and supportive of both the client and their family."),
 ],
 'experts_heading': 'Defining Our Specialist Support',
 'experts_paras': [
   f"Long-Term Condition Support is a specialist care solution designed for clients living with chronic health requirements, such as Parkinson's, stroke recovery, or other persistent health conditions. Unlike standard support, our approach is clinically informed, focusing on symptom management, medication administration, and maintaining physical health. As a CQC-rated provider, we work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure every client receives professional, high-standard care that prioritises comfort and clinical safety at home. By providing this professional support, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 ],
 'feature_heading': 'Expert Care, Real Results: How We Support Independence',
 'feature_text': f"True Homecare's Long-Term Condition Support provides the profound peace of mind that comes from knowing the client is clinically safe and expertly managed within their own home. By transitioning from the stress of navigating complex health needs alone to our structured, professional support, our clients experience a measurable improvement in their daily comfort and health outcomes. {TEAM} They ensure every individual receives the tailored, consistent attention they need to thrive safely, while providing family members with the essential respite and emotional relief they deserve.",
 'benefits_heading': 'Our Long-Term Condition Support Features',
 'benefits': [
   ('Clinical Medication Management', "Our staff undergo rigorous training to manage complex medication schedules accurately, reducing the risk of errors and ensuring consistent health maintenance for all our Long-Term Condition Support clients."),
   ('Personalised Symptom Monitoring', "We track subtle changes in health daily, providing early intervention and clear reporting to GPs, pharmacists, and district nurses. This is vital for managing progressive, long-term health conditions safely and effectively."),
   ('Specialised Mobility Support', "We utilise safe, approved transfer techniques and mobility aids—including support for Parkinson's clients—to prevent injury, ensuring the client moves with confidence and complete security within their own home."),
   ('Nutritional & Hydration Care', "Our team prepares nutritionally balanced meals tailored to specific dietary needs, supporting long-term physical health and the strength required for ongoing recovery and daily wellness."),
   ('Seamless Clinical Liaison', "We work as an extension of the existing medical team, coordinating effectively with district nurses, pharmacists, and consultants to provide a unified, safe care approach, strictly adhering to the Ethical Framework by Stockport Council."),
   ('Advanced Condition Training', "Every caregiver receives specific training for the client's condition, ensuring that support is knowledgeable, reactive to specific needs, and grounded in clinical best practices. For Dementia, one caregiver serves the client; because if there is a new carer, they cannot monitor and diagnose a client's health condition with consistency."),
 ],
 'phone_cta': 'Call us to find out more about Long-Term Condition Support',
 'why1': ('Why Choose True Homecare for Long-Term Condition Support', "True Homecare bridges the gap between highly personalised, compassionate support and strict regulatory excellence. Our services operate at the intersection of person-centred care and full CQC compliance, ensuring every client receives safe, professional assistance. By adhering to the Ethical Framework by Stockport Council and combining local expertise with national quality standards, we provide a reliable, high-standard alternative to residential settings."),
 'why2': ('Delivering Excellence in Long-Term Condition Support', "We are deeply committed to delivering compassionate, high-quality clinical support. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The safety, dignity, and wellbeing of our clients are our absolute top priorities. We strive for regulated excellence in everything we do—whether providing 24-hour support, waking nights, or assisting with companionship and outings like walks in the park—to ensure every client and their family member receives the emotional support and respite they deserve."),
 'careopts_heading': 'Related Services',
 'careopts_intro': 'Long-term care is a multifaceted journey that often requires flexible, complementary support. Explore our person-centred Companionship and premium 24-hour Live-in Care for a fully integrated care plan that supports the entire family.',
 'careopts_cards': [
   {'img': IMG_COMP, 'title': 'Person-Centred Companionship',
    'body': "Combat isolation and improve emotional wellbeing through meaningful social connection. Our companionship services go beyond simple visits; we focus on fostering genuine relationships that keep clients socially active, intellectually engaged, and emotionally supported in their own home. By providing this professional service, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
    'items': [
      ('Meaningful Social Engagement', "We facilitate active participation in hobbies, local outings, and community interests, ensuring our clients remain connected to the world around them and feel truly valued."),
      ('Emotional & Mental Support', "Our team provides empathetic listening and companionship that helps reduce feelings of loneliness and anxiety, promoting a more positive outlook and improved mental health."),
      ('Help with Daily Outings', "From park walks and movie visits to attending appointments or family gatherings, we provide the reliable support needed to maintain an independent and active lifestyle."),
    ], 'btn': ('Explore Companionship', '/services/companionship/')},
   {'img': IMG_LIVEIN, 'title': '24-Hour Live-in Care',
    'body': "Avoid the stress of moving to a residential setting. Our premium live-in care provides 24-hour support from a dedicated professional. Experience true one-to-one assistance that guarantees safety, dignity, and complete peace of mind in the client's own home.",
    'items': [
      ('Expert, Handpicked Caregivers', "We never do random placements. Every caregiver is rigorously vetted, undergoes comprehensive training, and is carefully matched to the client's personality, hobbies, and values."),
      ('Complex Needs & Conditions', f"{TEAM} We are clinically trained to manage advanced requirements safely at home, including specialist Alzheimer and Dementia Care, Stroke Care, palliative care, and support for Parkinson's clients."),
      ('Total Peace of Mind for Families', "Relieve the pressure on family members. Rest easy knowing the client is receiving continuous, compassionate supervision and immediate support, including waking nights or sleeping nights if required. We work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists, strictly adhering to the Ethical Framework by Stockport Council."),
    ], 'btn': ('Explore Live-in Care', '/services/live-in-care/')},
 ],
 'content_html': (
   '<h3><strong>Our Step-by-Step Care Delivery Process</strong></h3>'
   '<p>At True Homecare, we prioritise a transparent, clinically rigorous approach to providing Long-Term Condition Support and specialised home care. Our seamless process is designed to ensure that the client receives consistent, high-quality care that intelligently adapts to their evolving physical and emotional health requirements, while providing family members with the essential respite and peace of mind they deserve.</p>'
   '<h4><strong>1. Initial Clinical Assessment</strong></h4>'
   '<p>Our process begins with a comprehensive, free assessment in the client\'s own home, where our experienced Care Managers conduct a deep dive into the client\'s medical history and daily living needs. We engage directly with the family to identify the primary challenges of chronic disease management, ensuring we fully understand the clinical and emotional support required to maintain the client\'s safety, dignity, and independence.</p>'
   '<h4><strong>2. Bespoke Plan Creation</strong></h4>'
   '<p>We translate our assessment findings into a tailored, actionable roadmap specifically designed to address unique health goals. This roadmap coordinates essential tasks—such as medication management, mobility assistance, and nutritional planning—while ensuring the care plan aligns perfectly with the client\'s lifestyle. By focusing on premium private home care, we empower the client to thrive securely within their familiar surroundings.</p>'
   '<h4><strong>3. Dedicated Caregiver Matching</strong></h4>'
   f'<p>Unlike standard agencies, we believe Long-Term Condition Support is built on relationships. We perform a sophisticated matching process to pair the client with a skilled professional or caregiver who shares their personality, hobbies, and values. This ensures that the support provided is not only clinically effective but also personally enriching, fostering trust and long-term stability. {TEAM}</p>'
   '<h4><strong>4. Ongoing Monitoring & Proactive Review</strong></h4>'
   '<p>Quality care is never static. We provide continuous, proactive monitoring of health outcomes, strictly adhering to the Ethical Framework by Stockport Council. We regularly review and refine the support package based on real-time clinical progress and direct, open feedback from the family and the medical team, including GPs, pharmacists, and district nurses. This adaptive approach ensures that our professional care management remains effective, responsive, and perfectly synchronised with any changes in health.</p>'
   '<h2><strong>Home Care vs. Residential Care</strong></h2>'
   + table_html([
     'True Homecare protects your cherished independence',
     'We preserve your familiar, comforting home environment',
     'You receive dedicated, focused, one-to-one professional attention',
     'Our flexible care remains highly cost-effective daily',
     'We honour your unique, personal daily routine',
   ], header=('Care Criteria', 'True Homecare', 'Residential Care'))
 ),
 'faq_heading': 'Long-Term Condition Support FAQs',
 'faqs': [
   ('Who qualifies for Long-Term Condition Support?', f"Anyone requiring ongoing assistance with daily living or clinical health needs due to a persistent health condition qualifies for our support. {TEAM} We are ready to assist you."),
   ('How much does long-term care cost?', "Costs vary based on the specific level of need and the bespoke care package required. However, home care is often a more viable alternative to moving into a residential setting, allowing clients to maintain their independence in the comfort of their own home while providing family members with essential respite."),
   ('What triggers the need for long-term support?', "Support is usually identified when a professional assessment determines a client needs assistance with daily activities or medical management. Our Care Managers conduct a free in-home assessment to identify these specific needs and ensure a safe, dignified environment."),
   ('Are your care plans customisable?', "Yes, we create fully personalised care pathways. These are updated regularly to match specific clinical goals, mobility needs, and personal preferences, while strictly adhering to the Ethical Framework by Stockport Council."),
   ('Do you work with local GPs?', "Yes, we work in seamless collaboration with other healthcare professionals, including district nurses, GPs, hospitals, and pharmacists, to ensure comprehensive, high-standard care that prioritises clinical safety and wellbeing for the entire family."),
 ],
}

# ============ STROKE CARE ============
stroke = {
 'file': 'services__stroke-care.html', 'route': '/services/stroke-care/',
 'm_title': 'Stroke Care at Home in Stockport & Cheshire | True Homecare',
 'm_desc': 'Expert, CQC-rated stroke care and rehabilitation at home across Stockport, Wilmslow & Cheshire. Clinical support for mobility, speech and recovery. Call 0161 428 1989.',
 'hero_title': 'Stroke Care', 'hero_img': '/wp-content/uploads/2025/06/Stroke-Care-uk-truehomecare-e1750687057622.png',
 'hero_text': "True Homecare provides expert, bespoke Stroke Care at home for clients across Stockport, Wilmslow, and the wider Cheshire region. Our CQC-rated care professionals deliver high-quality, clinical support in the comfort of the client's home, ensuring they maintain independence, safety, and dignity during their recovery journey through our locally-trusted, clinical expertise. By providing this professional support, we offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 'process_heading': 'How do I arrange Stroke Care at Home?',
 'process_intro': "Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a safeguarding-compliant Stroke Care package, tailored perfectly to the client's recovery goals and clinical needs.",
 'process_cards': [
   ('1. Contact our Stroke Care Experts', "Get in touch with our Stockport and Wilmslow-based team at 01614281989 using our secure online enquiry form to discuss your family's specific options. Our dedicated support team is available 24/7 and aims to respond to all enquiries immediately to provide instant peace of mind. Whether you need Stroke Care or a combination of our other services—such as Companionship, Domiciliary Care, Long-Term Condition Support, or Respite Care—we are here to help."),
   ('2. Free In-Home Assessment within 24 hours', f"{TEAM} They will discuss your requirements, learn more about the client's medical history, current mobility, and daily routine, and carry out a free assessment in their own home. This helps us understand the exact level of 24-hour support required, including waking nights or sleeping nights, to ensure safety and independence."),
   ('3. Your bespoke Stroke Care package', "Our team will create a fully person-centred care plan based on exact clinical needs and rehabilitation goals. We strictly adhere to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff are carefully matched based on individual personality traits, professional expertise in rehabilitation, and specific health requirements. We work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure that our care is consistent, compassionate, and supportive of both the client and their family."),
 ],
 'experts_heading': 'Our Specialist Stroke Support',
 'experts_paras': [
   "Stroke Care at home is a specialist support solution designed for survivors needing assistance with physical mobility, speech, and cognitive recovery after a neurological event. Unlike standard support, our approach is clinically informed, focusing on immediate recovery needs, medication administration, and maintaining physical health. As a CQC-rated provider, we work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists to ensure every client receives professional, high-standard care that prioritises comfort and clinical safety. By providing this professional support, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 ],
 'feature_heading': 'Expert Care, Real Results: How We Support Independence',
 'feature_text': f"True Homecare's stroke rehabilitation at home provides the profound peace of mind that comes from knowing the client is clinically safe and expertly managed within their own home. By transitioning from the stress of navigating recovery alone to our structured, professional support, our clients experience a measurable improvement in their daily comfort, communication skills, and health outcomes. {TEAM} They ensure every individual receives the tailored, consistent attention they need to thrive safely, while providing family members with the essential respite and emotional relief they deserve.",
 'benefits_heading': 'Benefits of Stroke Care at Home',
 'benefits': [
   ('Clinical Medication Management', "Our staff undergo rigorous training to manage complex medication schedules accurately, reducing the risk of errors and ensuring consistent health maintenance during the vital recovery period for all our Stroke Care clients."),
   ('Personalised Symptom Monitoring', "We track subtle changes in health daily, providing early intervention and clear reporting to GPs, pharmacists, and district nurses. This is vital for managing post-stroke conditions safely and effectively."),
   ('Specialised Mobility Support', "We utilise safe, approved transfer techniques and mobility aids to prevent injury, ensuring the client moves with confidence and complete security within their own home."),
   ('Nutritional & Hydration Care', "Our team prepares nutritionally balanced meals tailored to specific dietary needs, supporting long-term physical health and the strength required for ongoing recovery and daily wellness."),
   ('Seamless Clinical Liaison', "We work as an extension of the existing medical team, coordinating effectively with speech therapists, consultants, GPs, and pharmacists to provide a unified, safe Stroke Care approach, strictly adhering to the Ethical Framework by Stockport Council."),
   ('Advanced Condition Training', "Every caregiver receives specific training for stroke recovery, ensuring that support is knowledgeable, reactive to specific needs, and grounded in current clinical best practices. For Dementia, one caregiver serves the client; because if there is a new carer, they cannot monitor and diagnose a client's health condition with consistency."),
 ],
 'phone_cta': 'Call us to find out more about Stroke Care',
 'why1': ('Why Choose True Homecare for Stroke Care', "True Homecare bridges the gap between highly personalised, compassionate support and strict regulatory excellence. Our services operate at the intersection of person-centred care and full CQC compliance, ensuring every client receives safe, professional assistance. By adhering to the Ethical Framework by Stockport Council and combining local expertise with national quality standards, we provide a reliable, high-standard alternative to residential settings for at-home Stroke Care."),
 'why2': ('Delivering Excellence in Stroke Care', "We are deeply committed to delivering compassionate, high-quality clinical support. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The safety, dignity, and wellbeing of our clients are our absolute top priorities. We strive for regulated excellence in everything we do—whether providing 24-hour support, waking nights, or assisting with companionship and outings like walks in the park—to ensure every client and their family member receives the emotional support and respite they deserve."),
 'careopts_heading': 'Related Services',
 'careopts_intro': "Stroke recovery is a multifaceted journey that often requires more than one type of support. To ensure the highest quality of life and sustained independence, True Homecare offers a range of professional home care services designed to complement every stroke recovery plan, whether they require short-term companionship or comprehensive 24-hour support.",
 'careopts_cards': [
   {'img': IMG_COMP, 'title': 'Person-Centred Companionship',
    'body': "Combat isolation and improve emotional wellbeing through meaningful social connection. Our companionship services focus on fostering genuine relationships that keep clients socially active, intellectually engaged, and emotionally supported in their own home.",
    'items': [
      ('Social Engagement', "We facilitate active participation in hobbies, community events, and local interests, ensuring clients remain connected to the world and feel truly valued."),
      ('Emotional Support', "Our team provides empathetic listening and consistent presence, helping to reduce feelings of loneliness and anxiety while fostering a positive outlook."),
      ('Outing Assistance', "From a stroll in the park to a movie or family gathering, we provide the reliable support needed to maintain an active lifestyle."),
    ], 'btn': ('Explore Companionship', '/services/companionship/')},
   {'img': IMG_LIVEIN, 'title': '24-Hour Live-in Care',
    'body': "Avoid the stress of moving to a residential setting. Our premium live-in care provides 24-hour support from a dedicated professional. Experience true one-to-one assistance that guarantees safety, dignity, and complete peace of mind.",
    'items': [
      ('24/7 Security', "Rest easy knowing a professional is present round-the-clock to manage safety, respond to emergencies, and provide continuous supervision, day and night."),
      ('Professional Companionship', "Beyond clinical needs, our team provides meaningful company, turning daily routines into positive interactions that enhance the client's overall quality of life."),
      ('Dedicated Assistance', "Receive unwavering, personalised support for all daily tasks—from medication management, performed in liaison with GPs and pharmacists, to personal hygiene and household help—tailored specifically to the client's unique requirements."),
    ], 'btn': ('Explore Live-in Care', '/services/live-in-care/')},
 ],
 'content_html': (
   '<h3><strong>The Pathway to Stroke Recovery at Home</strong></h3>'
   '<p>Recovering from a stroke requires a structured, phased approach to ensure safety and steady improvement. True Homecare guides survivors through a clear journey toward regained independence, while offering family members the essential respite and peace of mind they deserve.</p>'
   '<h4><strong>The Assessment Process</strong></h4>'
   '<p>Every journey begins with a comprehensive medical review and a detailed home safety check. We identify potential hazards and evaluate the living environment to ensure it is fully equipped to support a safe recovery.</p>'
   '<h4><strong>Developing the Care Plan</strong></h4>'
   "<p>We create a bespoke care plan focused on achievable milestones. This includes setting specific, measurable goals for improving mobility and restoring communication skills, tailored to the client's current abilities.</p>"
   '<h4><strong>Integrating Therapies</strong></h4>'
   f'<p>Recovery is most effective when coordinated. {TEAM} We work in close collaboration with speech and physical therapists, GPs, and district nurses to ensure that clinical exercises are consistently reinforced during daily home care.</p>'
   '<h4><strong>Monitoring Progress</strong></h4>'
   "<p>Recovery is not linear. We conduct regular reviews to monitor achievements and adjust the care plan as needs evolve, strictly adhering to the Ethical Framework by Stockport Council to ensure the support remains aligned with the client's progress.</p>"
   '<h2><strong>Home Care vs. Residential Care</strong></h2>'
   '<p>We provide care that allows your loved one to stay in their own home rather than moving to a facility, ensuring better mental and physical health outcomes.</p>'
   + table_html([
     'Retain independence in a familiar, comfortable environment',
     'Dedicated one-to-one matched caregiver relationship',
     'Ability to keep existing pets and maintain lifelong daily routines',
     'Complete flexibility over meal choices and family visiting hours',
     'A highly cost-effective alternative to residential care',
   ])
 ),
 'faq_heading': 'Stroke Care FAQs',
 'faqs': [
   ('Can clients recover better at home?', "Yes, a familiar environment provides psychological comfort and clinical advantages, often accelerating the recovery process. By remaining at home, clients maintain their lifelong habits, which supports mental wellbeing while providing family members with the peace of mind that their relative is receiving professional, compassionate care."),
   ('What professional support is needed after a stroke?', f"Recovery requires multidisciplinary support. {TEAM} We work in seamless collaboration with speech and physical therapists, GPs, pharmacists, and district nurses to provide an integrated approach to rehabilitation."),
   ('How do you manage mobility challenges?', "We utilise safe, approved transfer techniques and mobility aids to ensure movement is secure, helping clients regain strength and confidence within their own home. All mobility support is strictly monitored to prevent injury and promote independence."),
   ('When is live-in care recommended?', "24-hour support is recommended when safety triggers—such as high fall risks, the need for complex medication management, or the requirement for waking nights or sleeping nights—make visiting support insufficient. This level of care ensures constant safety and immediate emergency support."),
   ('How is the home adapted for stroke recovery?', "As part of our initial assessment, our experienced Care Managers evaluate the living environment to identify and mitigate risks. While we do not perform structural construction, we advise on the installation of accessibility features—such as grab rails and ramps—to remove hazards and ensure a safe, navigable environment for the client. We strictly adhere to the Ethical Framework by Stockport Council in all our operations."),
 ],
}

# ============ PARKINSON'S CARE ============
parkinsons = {
 'file': 'services__parkinsons-care.html', 'route': '/services/parkinsons-care/',
 'm_title': "Parkinson's Care at Home in Stockport & Wilmslow | True Homecare",
 'm_desc': "Premium, CQC-rated Parkinson's care at home across Stockport, Wilmslow & Cheshire. Specialist support for medication, mobility & symptoms. Call 0161 428 1989.",
 'hero_title': "Parkinson's Care at Home", 'hero_img': '/wp-content/uploads/2025/06/Parkinsons-Car-uk-truehomecare-e1750678402255.webp',
 'hero_text': "True Homecare provides premium, bespoke Parkinson's Care at home, designed to help clients safely maintain their independence. Offering person-centred professional support, we provide specialised local expertise specifically in Wilmslow and Stockport, ensuring clients receive high-quality, one-to-one care in their own familiar, comfortable surroundings. By providing this professional service, we also offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 'process_heading': "How do I arrange Parkinson's Care at Home?",
 'process_intro': "Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a safeguarding-compliant Parkinson's home care package, tailored perfectly to the client's clinical and personal needs.",
 'process_cards': [
   ("1. Contact our Parkinson's Care Experts", "Get in touch with our team at 01614281989 or use our secure online enquiry form to discuss your family's specific options. Our support team is available 24/7 to provide instant peace of mind."),
   ('2. Free In-Home Assessment', f"{TEAM} They will discuss your requirements, learn more about the client's specific symptoms and daily routine, and carry out a free assessment in their own home to ensure complete safety and comfort."),
   ("3. Your Bespoke Parkinson's Care Package", "We create a fully person-centred care package. We strictly adhere to the Ethical Framework by Stockport Council and work in seamless collaboration with healthcare professionals like GPs and district nurses. We never do random placements; all of our CQC-rated staff are matched based on specific expertise in managing motor fluctuations, cognitive health, and complex mobility requirements."),
 ],
 'experts_heading': 'See What Our Experts Can Do',
 'experts_paras': [f"True Homecare's specialist Parkinson's Care provides profound peace of mind. By transitioning from the stress of navigating a progressive condition alone to our structured, professional support, our clients experience a measurable improvement in their daily quality of life. {TEAM} They ensure every individual receives the tailored attention they need to thrive independently in their familiar surroundings."],
 'feature_heading': "Parkinson's Care Your Family Can Trust",
 'feature_text': "Balancing professional responsibilities with the care of a loved one living with Parkinson's often leads to severe caregiver stress. We alleviate this emotional burden, providing the ultimate relief of knowing your loved ones are safe, dignified, and well-supported. Our absolute commitment to quality is backed by our Care Quality Commission (CQC) rated ‘Good’ standard, ensuring your family receives highly reliable, safeguarding-compliant Parkinson's home care services.",
 'benefits_heading': "Comprehensive Parkinson's Care Support Features",
 'benefits': [
   ('Personalised Medication Management', "We ensure health stability through the safe administration of prescriptions in liaison with GPs and pharmacists, maintaining strict adherence to complex care plans."),
   ('Proactive Fall Prevention & Mobility', "We provide specialised safety measures and transfer techniques, strictly adhering to the Ethical Framework by Stockport Council to ensure mobility is secure."),
   ('Nutritional & Hydration Support', "Our team provides tailored meal preparation designed to manage symptoms like tremors or swallowing difficulties while promoting a healthy appetite."),
   ('Specialised Cognitive Engagement', "We provide engaging activities specifically designed to maintain mental sharpness and reduce the anxiety often associated with Parkinson's progression."),
   ('Companionship and Social Engagement', "We actively combat loneliness by providing consistent emotional support and facilitating local community outings, helping clients stay socially active."),
   ('Household Management', "To maintain a stress-free environment, we assist with shopping, errands, and light housekeeping, ensuring a consistently safe and organised living space."),
 ],
 'phone_cta': "Call us to find out more about Parkinson's Care",
 'why1': ("Why True Homecare is the First Choice for Parkinson's Care", "True Homecare delivers CQC-rated, personalised Parkinson's Care rooted in dignity, respect, and clinical professionalism. Beyond our years of experience, we strictly adhere to the Ethical Framework by Stockport Council and work in seamless collaboration with local healthcare professionals. We provide the high-quality support every client deserves to live independently and safely at home."),
 'why2': ("Delivering Perfection in Parkinson's Care", "We are deeply committed to delivering compassionate, high-quality home care for Parkinson's. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The safety, dignity, and wellbeing of our clients are our absolute top priorities, and we strive for regulated excellence in everything we do."),
 'careopts_heading': 'Complementary Care Solutions',
 'careopts_intro': "We understand that managing complex health needs is a multifaceted journey that often requires flexible, targeted support. To ensure the highest quality of life and sustained independence, we offer a range of professional home care services designed to complement your Parkinson's care plan. Explore our specialized solutions below, each tailored to provide the compassionate, expert assistance your loved one deserves, whether they require specialized memory support or essential short-term relief.",
 'careopts_cards': [
   {'img': IMG_DEM, 'title': 'Alzheimer and Dementia Care',
    'body': "Keep clients safe in their most familiar surroundings. Our bespoke support provides expert, CQC-rated assistance tailored to exact schedules. We actively manage the complexities of memory loss so clients can maintain their routine securely and happily at home.",
    'items': [
      ('Consistent, Familiar Routine', "Routine is critical. Our dedicated caregivers structure their support around existing habits to minimise confusion, reduce anxiety, and create a calm environment."),
      ('Specialist Memory Support', "Our staff undergo rigorous, specialised training. We expertly manage symptoms like “sundowning,” assist with cognitive stimulation exercises, and ensure all medications—managed in collaboration with GPs and pharmacists—are taken safely and on time."),
      ('Essential Respite for Families', "Caring for a relative with memory loss is exhausting. Our flexible care gives family members crucial time to rest and recharge, knowing the client is in safe, professional hands."),
    ], 'btn': ('Request Dementia Assessment', '/services/dementia-and-alzheimer-care/')},
   {'img': IMG_RESP, 'title': 'Private Respite Care at Home',
    'body': "Need a temporary break from caregiving? Our private, CQC-rated respite care provides short-term, professional relief. We step in seamlessly to ensure clients remain safe and comfortable, allowing family members to rest and recharge with complete peace of mind.",
    'items': [
      ('Seamless Routine Transition', "We mirror your exact routine. From complex medication schedules to preferred meal times, our professional caregivers ensure a flawless handover so the client feels secure and undisturbed."),
      ('Highly Flexible Short-Term Cover', "Whether you need a few hours a week, emergency overnight support, or full live-in care for a holiday, our bespoke packages adapt to your exact schedule."),
      ('Total Peace of Mind for Families', "Step away knowing your relative is supported by rigorously vetted, clinically trained experts. We actively manage all personal care and companionship, giving you the essential break you deserve."),
    ], 'btn': ('Book Respite Cover', '/services/respite-care/')},
 ],
 'content_html': (
   "<h3><strong>The Pathway to Parkinson's Care at Home</strong></h3>"
   "<p>Managing Parkinson's requires a structured, phased approach to ensure safety, symptom stability, and a high quality of life. True Homecare guides clients through a clear journey toward maintaining independence while providing family members with the essential respite and peace of mind they deserve.</p>"
   '<h4><strong>The Initial Assessment Process</strong></h4>'
   '<p>Every journey begins with a comprehensive medical review and a detailed home safety check. We identify potential hazards related to tremors or balance issues and evaluate the living environment to ensure it is fully equipped to support safety and mobility.</p>'
   "<h4><strong>Developing the Parkinson's Care Plan</strong></h4>"
   "<p>We create a bespoke care plan focused on achievable milestones. This includes setting specific, measurable goals for managing medication schedules, improving physical rigidity, and maintaining daily living skills, all tailored to the client's current abilities.</p>"
   '<h4><strong>Integrating Therapeutic Support</strong></h4>'
   "<p>Effective Parkinson's Care is most successful when coordinated. Our team, comprised of skilled professionals, care managers, care coordinators, and caregivers who are experts in palliative home care, works in close collaboration with physiotherapists, occupational therapists, and speech therapists to ensure that clinical exercises are consistently reinforced.</p>"
   '<h4><strong>Ongoing Monitoring &amp; Adaptation</strong></h4>'
   "<p>Living with Parkinson's is not linear. We conduct regular, proactive reviews, strictly adhering to the Ethical Framework by Stockport Council, to monitor symptoms and adjust the care plan as needs evolve.</p>"
   '<h2><strong>Home Care vs. Residential Care</strong></h2>'
   + table_html([
     'Maintain independence in familiar surroundings',
     'Dedicated one-to-one matched caregiver relationship',
     'Consistent professional fostering deep emotional bonds',
     'Maintaining social ties within the local community',
     'Cost-effective scaling of care hours as needs evolve',
   ], header=('Criteria', 'True Homecare', 'Residential Care'))
 ),
 'faq_heading': "Parkinson's Care FAQs",
 'faqs': [
   ("What is involved in Parkinson's home care?", "It includes medication management, mobility support, and symptom monitoring tailored to manage tremors and fluctuating motor skills."),
   ("When should I start Parkinson's care?", "Ideally, early to mid-stage, to help the client maintain their independence and manage symptoms proactively, while providing family members with essential relief."),
   ('How do you ensure a good caregiver match?', "We pair caregivers with specific clinical expertise in Parkinson's and personality traits that align with the client's lifestyle."),
   ('What is the role of the Care Manager?', "They act as the bridge between family and the care team, ensuring CQC standards are met, strictly adhering to the Ethical Framework by Stockport Council, and ensuring care plans evolve as needed."),
   ("Can your Parkinson's support scale up?", "Yes, our care plans are highly scalable, allowing us to add more hours, waking nights, or sleeping nights as the condition progresses."),
 ],
}

# ============ DEMENTIA & ALZHEIMER'S CARE ============
dementia = {
 'file': 'services__dementia-and-alzheimer-care.html', 'route': '/services/dementia-and-alzheimer-care/',
 'm_title': "Dementia & Alzheimer's Care at Home | True Homecare",
 'm_desc': "Expert, CQC-rated dementia and Alzheimer's care at home across Stockport, Wilmslow & Cheshire. Specialist memory support, routine and safety. Call 0161 428 1989.",
 'hero_title': "Dementia & Alzheimer's Care at Home", 'hero_img': '/wp-content/uploads/2025/06/dementia-care-alzhemier-care-truehomecare-uk-e1750667273455-1024x683.png',
 'hero_text': "True Homecare provides expert, bespoke Alzheimer and Dementia Care at home for clients across Stockport, Wilmslow, and the wider Cheshire region. Our CQC-rated care professionals deliver high-quality, clinical support in the comfort of the client's home, ensuring they maintain dignity, safety, and a sense of belonging. By providing this professional service, we offer essential respite and emotional relief to family members, ensuring you can return to your roles as family rather than full-time caregivers.",
 'process_heading': "How do I arrange Dementia and Alzheimer's Care at Home?",
 'process_intro': "Our local Cheshire and Greater Manchester team will guide you seamlessly through the process of arranging a safeguarding-compliant care package, tailored perfectly to the client's unique cognitive requirements, personal history, and daily needs.",
 'process_cards': [
   ('1. Contact our Dementia Care Experts', "Get in touch with our Stockport and Wilmslow-based team at 01614281989 using our secure online enquiry form to discuss your family's specific support options. Our dedicated support team is available 24/7 to provide immediate guidance and peace of mind."),
   ('2. Free In-Home Assessment within 24 hours', f"{TEAM} They will discuss your requirements, learn more about the client's specific stage of memory loss and their daily routine, and carry out a free assessment in their own home to identify the specialised support and safety measures required."),
   ('3. Your bespoke Dementia Care package', "Our team will create a fully person-centred care plan based on exact clinical needs and preferences, strictly adhering to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff are carefully matched based on their specialised training, personality, and the specific cognitive support required. Please note: for dementia, one caregiver serves the client; because if there is a new carer, they cannot monitor and diagnose a client's health condition with consistency. We work in seamless collaboration with healthcare professionals like GPs, district nurses, and pharmacists to ensure that our care is consistent and compassionate."),
 ],
 'experts_heading': 'Compassionate Dementia Care',
 'experts_paras': ["Dementia care at home is a specialist support solution designed for individuals living with progressive cognitive conditions, including Alzheimer's disease, vascular dementia, and other memory-related requirements. Unlike standard home care, our approach is clinically informed, focusing on cognitive stimulation, routine preservation, and emotional regulation. As a CQC-rated provider, we work closely with GPs and memory specialists to ensure your relative receives professional, high-standard care that prioritises comfort and safety."],
 'feature_heading': 'Expert Care, Real Results: How We Support Independence',
 'feature_text': "True Homecare's specialist dementia care provides the profound peace of mind that comes from knowing your loved one is clinically safe and expertly managed within their own home. By transitioning from the stress of navigating memory decline alone to our structured, professional support, our clients experience a measurable improvement in their daily comfort and quality of life. Our expert teams ensure every individual receives the consistent, patient attention they need to thrive securely and confidently in their familiar surroundings.",
 'benefits_heading': "Our Dementia & Alzheimer's Care Features",
 'benefits': [
   ('Consistent Routine Management', "We prioritise daily routines to provide stability and reduce confusion, which is essential for managing the emotional fluctuations common in dementia and Alzheimer's care."),
   ('Specialist Memory Support', "Our carers use cognitive stimulation techniques to maintain mental sharpness and engage your loved one in activities that foster joy, recognition, and emotional connection."),
   ('Safe Environment Monitoring', "We conduct regular home safety checks to prevent accidents and wandering, ensuring your loved one is secure while enjoying their freedom within the home."),
   ('Nutritional & Hydration Care', "We provide personalised mealtime support, ensuring your loved one receives the nutrition they need, even if they experience challenges with appetite or swallowing."),
   ('Seamless Clinical Liaison', "We act as an extension of your medical team, coordinating closely with GPs and specialists to ensure that all health changes are tracked and addressed immediately."),
   ('Advanced Dementia Training', "Every carer receives specific, mandatory training in dementia and Alzheimer's, ensuring their approach is knowledgeable, compassionate, and grounded in the latest clinical best practices."),
 ],
 'phone_cta': 'Call us to find out more about Dementia Care',
 'why1': ('Why Choose True Homecare for Dementia Care', "True Homecare bridges the gap between highly personalised, compassionate support and strict regulatory excellence. Our services operate at the intersection of person-centred care and full CQC compliance, ensuring every client receives safe, professional assistance. By adhering to the UK Ethical Framework and combining local expertise with national quality standards, we provide a reliable, high-standard alternative to residential facilities for at-home dementia care."),
 'why2': ('Delivering Excellence in Dementia Care', "We are deeply committed to delivering compassionate, high-quality clinical support. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). Your loved one's safety, dignity, and wellbeing are our absolute top priorities, and we strive for regulated excellence in everything we do, every single day."),
 'careopts_heading': 'Dementia Related Services Available',
 'careopts_intro': "We understand that managing complex health needs is a multifaceted journey that often requires flexible, targeted support. To ensure the highest quality of life and sustained independence, we offer a range of professional home care services designed to complement your dementia and Alzheimer's care plan. Explore our specialized solutions below, each tailored to provide the compassionate, expert assistance your loved one deserves.",
 'careopts_cards': [
   {'img': IMG_COMP, 'title': 'Person-Centred Companionship',
    'body': "Combat isolation and improve emotional wellbeing through meaningful social connection. Our companionship services go beyond simple visits; we focus on fostering genuine relationships that keep your loved one socially active, intellectually engaged, and emotionally supported in their own home.",
    'items': [
      ('Social Engagement', "We facilitate active participation in hobbies, community events, and local interests, ensuring your loved one remains connected to the world around them and feels truly valued."),
      ('Emotional Support', "Our carers provide empathetic listening and a consistent presence, which helps reduce feelings of loneliness, anxiety, and confusion, promoting a more positive outlook and improved mental health."),
      ('Outing Assistance', "From park walks and café visits to attending appointments or family gatherings, we provide the reliable support needed to maintain an independent and active lifestyle."),
    ], 'btn': ('Explore Companionship', '/services/companionship/')},
   {'img': IMG_LIVEIN, 'title': '24-Hour Live-in Care',
    'body': "Avoid the stress of moving to a residential facility. Our premium live-in care provides 24/7 support from a dedicated professional who lives with you. Experience true one-to-one assistance that guarantees safety, dignity, and complete peace of mind in your own beloved home.",
    'items': [
      ('24/7 Security', "Rest easy knowing a professional is present round-the-clock to manage safety, respond to emergencies immediately, and provide continuous supervision, day and night."),
      ('Professional Companionship', "Beyond clinical needs, your carer provides meaningful company, turning daily routines into positive interactions that enhance your loved one's overall quality of life and cognitive stimulation."),
      ('Dedicated Assistance', "Receive unwavering, personalised support for all daily tasks—from medication management and personal hygiene to household help—tailored specifically to your loved one's unique requirements."),
    ], 'btn': ('Explore Live-in Care', '/services/live-in-care/')},
 ],
 'content_html': (
   '<h3><strong>Our Approach to Person-Centred Dementia Care</strong></h3>'
   "<p>At True Homecare, we prioritise a transparent, clinically rigorous approach to providing specialized dementia and Alzheimer's support. Our seamless process is designed to ensure that your loved one receives consistent, high-quality care that intelligently adapts to their evolving cognitive and emotional health requirements.</p>"
   '<h4><strong>Initial Clinical Assessment</strong></h4>'
   "<p>Our process begins with a comprehensive, free assessment in your own home, where our experienced Care Managers conduct a deep dive into your loved one's specific medical history, stage of cognitive decline, and daily living needs. We engage directly with you and your family to identify the primary challenges of memory loss, ensuring we fully understand the clinical and emotional support required to maintain your loved one's safety, dignity, and independence.</p>"
   '<h4><strong>Bespoke Plan Creation</strong></h4>'
   "<p>We translate our assessment findings into a tailored, actionable roadmap for dementia care at home, specifically designed to address your loved one's unique health goals. This roadmap coordinates essential tasks—such as routine stabilization, nutritional planning, and medication management—while ensuring the care plan aligns perfectly with their lifelong habits. By focusing on premium private home care, we empower your loved one to thrive securely within their familiar surroundings.</p>"
   '<h4><strong>Ongoing Monitoring</strong></h4>'
   "<p>Quality dementia care is never static, which is why we provide continuous, proactive monitoring of your loved one's health outcomes. We regularly review and refine your dementia care package based on real-time cognitive progress and direct, open feedback from you and your medical team. This adaptive approach ensures that our professional care management remains effective, responsive, and perfectly synchronized with any changes in your loved one's long-term memory support needs.</p>"
   '<h2><strong>Home Care vs. Residential Care</strong></h2>'
   '<p>We provide care that allows your loved one to stay in their own home rather than moving to a facility, ensuring better mental and physical health outcomes.</p>'
   + table_html([
     'Retain independence in a familiar, comfortable environment',
     'Dedicated one-to-one matched carer relationship',
     'Ability to keep existing pets and maintain lifelong daily routines',
     'Complete flexibility over meal choices and family visiting hours',
     'Cost-effective scaling based purely on the exact hours of support needed',
   ], header=('Dementia Care Criteria & Benefits', 'True Homecare', 'Residential Care'))
 ),
 'faq_heading': "Dementia & Alzheimer's Care FAQs",
 'faqs': [
   ('Can someone with dementia thrive at home?', "Yes; staying in a familiar environment is often recommended as it reduces confusion and helps maintain memory-based routines."),
   ('How do you handle “sundowning” or restlessness?', "Our carers are trained to manage evening restlessness by providing calm, quiet activities and a structured routine to reduce anxiety."),
   ("Are your carers trained specifically in Alzheimer's?", "Yes, all our carers undergo rigorous, specialist dementia training to ensure they understand the nuances of memory-loss support."),
   ('Do you involve family in the care plan?', "Absolutely; we believe family involvement is crucial, and we keep you informed through regular reporting and transparent communication."),
   ('How does care scale as dementia progresses?', "We provide flexible, scalable support, allowing us to increase care hours or transition to live-in support as your loved one's needs increase."),
 ],
}

# ============ DOMICILIARY CARE ============
domiciliary = {
 'file': 'services__domiciliary-care.html', 'route': '/services/domiciliary-care/',
 'm_title': 'Domiciliary Care in Stockport & Wilmslow | True Homecare',
 'm_desc': 'CQC-rated domiciliary care at home across Stockport, Wilmslow & Cheshire. Personal care, medication, meals, mobility and companionship that keeps loved ones independent. Call 0161 428 1989.',
 'hero_title': 'Domiciliary Care', 'hero_img': '/wp-content/uploads/2025/07/Domiciliary-Care-Uk-Truehomecare-e1751638985436.png',
 'hero_text': "Domiciliary care provides tailored professional support delivered directly in the client's own home. It is designed for individuals who wish to live independently but require assistance with daily tasks to maintain their safety, dignity, and wellbeing.",
 'process_heading': 'How do I arrange Domiciliary Care?',
 'process_intro': "Our local team will guide you seamlessly through the process of arranging a safeguarding-compliant care package, tailored perfectly to the client's clinical and personal requirements.",
 'process_cards': [
   ('Contact our Domiciliary Care Experts', "Get in touch with our Stockport and Wilmslow-based team on 01614281989 or use our secure online enquiry form to discuss your family's specific options. Our dedicated team handles all private care enquiries promptly, walking you through the baseline choices for your relative to provide immediate guidance and peace of mind on our home care services, including Stroke Care, Long-Term Condition Support, or Respite Care."),
   ('Free In-Home Assessment within 24 Hours', "Our team will visit to discuss your requirements, learn more about the client's specific health conditions, daily routine, and overall mental health. We conduct a free assessment in their own home to identify the specialised and emotional support, as well as safety measures, required to keep them comfortable."),
   ('Your Bespoke Care Alignment', "We create a person-centred care package that strictly adheres to the Ethical Framework by Stockport Council. We never do random placements; all of our CQC-rated staff hold relevant UK certifications and qualifications and are carefully paired with clients based on physical needs, cognitive requirements, personality traits, and shared hobbies to ensure consistent emotional support—including tailored support for Parkinson's clients."),
 ],
 'experts_heading': 'Expert Care, Real Results: How We Support Independence',
 'experts_paras': ["True Homecare's professional domiciliary care provides the profound peace of mind that comes from knowing your relative is safe, dignified, and expertly supported within their own home. By transitioning from the stress of cold clinical settings to our personalised, dedicated in-home care, our clients experience a measurable improvement in their daily quality of life, physical comfort, and emotional wellbeing, allowing them to age in place safely."],
 'feature_heading': 'Domiciliary Care Your Family Can Trust',
 'feature_text': "Balancing professional responsibilities with the care of a relative living with complex health needs often leads to severe caregiver stress and family burden. We alleviate this emotional burden, providing the ultimate relief of knowing your relative is safe, dignified, and well-supported with dedicated emotional support.",
 'benefits_heading': 'Comprehensive Domiciliary Support Elements',
 'benefits': [
   ('Medication Management', "Our caregivers ensure prescriptions are taken accurately and on time. We assist with reminders, dosage tracking, and coordinating with pharmacies to prevent errors and maintain health stability, tracking routines in line with advice from bodies like Diabetes UK."),
   ('Personal Hygiene and Grooming', "We provide dignified support with bathing, dressing, and oral care. Our staff helps clients maintain their personal grooming standards, promoting confidence and physical wellbeing."),
   ('Nutritional Support and Meal Preparation', "Caregivers plan and prepare balanced meals tailored to dietary requirements. We provide assistance with eating and hydration to ensure all nutritional needs and physical health goals are met daily."),
   ('Mobility Assistance', "We help clients move safely around their homes and provide transportation support. This includes assistance with walking aids to reduce fall risk, support independent living, and maintain safety, under the guidance of the United Kingdom Homecare Association (UKHCA) and the Royal College of Nursing (RCN)."),
   ('Companionship Services', "Beyond physical needs, we provide emotional support and companionship. Our team engages clients in meaningful conversation and social activities to combat loneliness and isolation."),
   ('Household Management', "We assist with essential daily chores, including light cleaning, laundry, and organising. This ensures a safe, tidy, and stress-free living environment for our clients."),
 ],
 'phone_cta': 'Call us to find out more about Domiciliary Care',
 'why1': ('Why True Homecare is the First Choice for Domiciliary Care', "True Homecare delivers highly personalised domiciliary care rooted in dignity, respect, and deep community integration. Beyond our years of operational experience, we ensure that our care coordination seamlessly interfaces with your existing local medical networks. Our services operate at the intersection of person-centred care and full CQC compliance. We strictly adhere to the Ethical Framework by Stockport Council, ensuring our support is both locally trusted and held to the highest regulatory standards."),
 'why2': ('Delivering Perfection in Domiciliary Care', "We are deeply committed to delivering compassionate, high-quality domiciliary care services. True Homecare is proud to have achieved a ‘Good’ rating from the Care Quality Commission (CQC). The safety, dignity, and wellbeing of our clients are our absolute top priorities, and we strive for regulated excellence in everything we do. We work alongside other healthcare professionals like district nurses, GPs, hospitals, and pharmacists."),
 'careopts_heading': 'Specialist Domiciliary Care Options',
 'careopts_intro': "Explore the complementary services that work seamlessly alongside domiciliary care to provide a fully integrated, person-centred plan for your loved one.",
 'careopts_cards': [
   {'img': IMG_COMP, 'title': 'Person-Centred Companionship',
    'body': "Combat isolation and improve emotional wellbeing through meaningful social connection. Our companionship services focus on fostering genuine relationships that keep clients socially active, intellectually engaged, and emotionally supported in their own home.",
    'items': [
      ('Social Engagement', "We facilitate active participation in hobbies, community events, and local interests, ensuring clients remain connected to the world and feel truly valued."),
      ('Emotional Support', "Our team provides empathetic listening and consistent presence, helping to reduce feelings of loneliness and anxiety while fostering a positive outlook."),
      ('Outing Assistance', "From a stroll in the park to a movie or a family gathering, we provide the reliable support you need to maintain an active lifestyle."),
    ], 'btn': ('Explore Companionship', '/services/companionship/')},
   {'img': IMG_LIVEIN, 'title': '24-Hour Live-in Care',
    'body': "Avoid the stress of moving to a residential setting. Our premium live-in care provides 24-hour support from a dedicated professional. Experience true one-to-one assistance that guarantees safety, dignity, and complete peace of mind.",
    'items': [
      ('24/7 Security', "Rest easy knowing a professional is present round-the-clock to manage safety, respond to emergencies, and provide continuous supervision, day and night."),
      ('Professional Companionship', "Beyond clinical needs, our team provides meaningful company, turning daily routines into positive interactions that enhance the client's overall quality of life."),
      ('Dedicated Assistance', "Receive unwavering, personalised support for all daily tasks—from medication management, performed in liaison with GPs and pharmacists, to personal hygiene and household help—tailored specifically to the client's unique requirements."),
    ], 'btn': ('Explore Live-in Care', '/services/live-in-care/')},
 ],
 'content_html': (
   '<h3><strong>Our Approach to Person-Centred Domiciliary Care</strong></h3>'
   '<h4><strong>The Step-by-Step Care Planning Process</strong></h4>'
   '<p>We ensure a seamless transition to domiciliary care through a structured onboarding process, providing in-home care that prioritises independence and dignity.</p>'
   '<h4><strong>1. Initial Consultation &amp; Needs Analysis</strong></h4>'
   "<p>A detailed needs analysis to understand the client's preferences, health conditions, and personal requirements. We also discuss how our home care services can provide essential respite and emotional support for family members, protecting them from caregiver burnout.</p>"
   '<h4><strong>2. Risk &amp; Safety Assessment</strong></h4>'
   "<p>A comprehensive evaluation of the home environment to ensure safety, mitigate hazards, and plan for specific at-home care needs, such as mobility support or palliative care home requirements.</p>"
   '<h4><strong>3. Plan Integration</strong></h4>'
   "<p>The creation of a personalised strategy tailored to the client's specific daily routines—including support for waking nights, sleeping nights, or outings such as taking out for a walk in the park, cinema visits, or hospital visits.</p>"
   '<h4><strong>4. Carer Matching &amp; Quality Monitoring</strong></h4>'
   '<p>Our care coordinators ensure our staff undergo rigorous regulatory screening. All staff pass comprehensive DBS checks and professional background screening. This approach guarantees that behavioural trends are correctly tracked by a familiar face. Our nursing oversight includes Registered Nurses (RNs) to manage clinical needs, and continuous oversight maintains the high standards of our domiciliary care.</p>'
   '<h4><strong>5. Family Collaboration &amp; Medical Liaison</strong></h4>'
   "<p>We maintain transparent communication channels and conduct regular care reviews with family members to ensure our home care services evolve alongside the client's needs.</p>"
   '<h2><strong>Domiciliary Care Service Comparison</strong></h2>'
   + table_html([
     'We protect your cherished independence and personal identity.',
     'We preserve your familiar, comforting home environment.',
     'You receive dedicated, focused, one-to-one professional attention.',
     'Our flexible care remains highly cost-effective daily.',
     'We honour your unique, personal daily routine.',
   ], header=('Care Criteria', 'True Homecare', 'Residential Care'))
 ),
 'faq_heading': 'Domiciliary Care FAQs',
 'faqs': [
   ('What is domiciliary care exactly?', "Domiciliary care is professional health and social care provided in a client's own home. It involves tailored support ranging from basic companionship and domestic help to complex personal care and medication management, allowing individuals to live independently."),
   ('Who is eligible for this type of support?', "Anyone requiring assistance to maintain their safety, mental health, and wellbeing at home is eligible. This typically includes seniors, individuals with progressive health conditions, or those recovering from hospital stays."),
   ('How does CQC inspection work for home care?', "The Care Quality Commission (CQC) conducts regular inspections to ensure providers meet fundamental standards of safety and quality. They review care records, interview staff and clients, and monitor outcomes to maintain a registered rating. True Homecare is proud to hold a ‘Good’ rating."),
   ('How do I arrange a first assessment?', "To begin, contact us to schedule a home visit. Our specialists will evaluate physical and emotional needs, discuss preferences, and use this information to build a bespoke care plan. Contact our Stockport and Wilmslow team directly on 01614281989 to arrange a free assessment within 24 hours."),
 ],
}

# ============ BUILD ALL ============
configs = [livein, longterm, stroke, parkinsons, dementia, domiciliary]
manifest = json.load(open(MANIFEST))
mmap = {m['route']: m for m in manifest}
for cfg in configs:
    f = build(cfg)
    print('BUILT', f)
    if cfg['route'] in mmap:
        mmap[cfg['route']]['title'] = cfg['m_title']
        mmap[cfg['route']]['description'] = cfg['m_desc']
json.dump(manifest, open(MANIFEST, 'w'), indent=1, ensure_ascii=False)
print('manifest updated')
