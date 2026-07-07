// Global site config for True Homecare

export const site = {
  name: 'True Homecare',
  tagline: 'care you can trust',
  phone: '0161 428 1989',
  phoneHref: 'tel:+441614281989',
  email: 'info@truehomecare.co.uk',
  hoursNote: 'Available 24/7',
  regNo: '7912253',
  cqc: 'Registered by the Care Quality Commission',
  ctaLabel: 'Request an Assessment',
  ctaHref: '/contact-us/',
  careerFormUrl: 'https://thc.techvando.com/',
  social: {
    facebook: 'https://www.facebook.com/',
    twitter: 'https://twitter.com/',
    linkedin: 'https://www.linkedin.com/',
  },
};

// Trustindex review widgets (loader script IDs)
export const trustindex = {
  heroBadge: '1680ea95433d93916f2631ab73c', // small rating badge (hero)
  reviewsWidget: '22dae5e5443f93905376a6cb72a', // full reviews section
};

// Primary navigation
export const nav = [
  { label: 'Locations', href: '/locations/' },
  {
    label: 'Services',
    href: '/services/',
    children: [
      { label: 'Personal Care', href: '/services/personal-care/' },
      { label: 'Dementia & Alzheimer’s Care', href: '/services/dementia-and-alzheimer-care/' },
      { label: 'Domiciliary Care', href: '/services/domiciliary-care/' },
      { label: 'Companionship', href: '/services/companionship/' },
      { label: 'Live-in Care', href: '/services/live-in-care/' },
      { label: 'Overnight Care', href: '/services/overnight-care/' },
      { label: 'Palliative Care', href: '/services/palliative-care/' },
      { label: 'Respite Care', href: '/services/respite-care/' },
    ],
  },
  {
    label: 'About',
    href: '/about-us/',
    children: [
      { label: 'About Us', href: '/about-us/' },
      { label: 'Blog', href: '/blog/' },
      { label: 'Contact Us', href: '/contact-us/' },
    ],
  },
  { label: 'Career', href: '/career/' },
];

// Footer link columns
export const footerLinks = {
  about: [
    { label: 'Locations', href: '/locations/' },
    { label: 'Contact Us', href: '/contact-us/' },
    { label: 'Blog', href: '/blog/' },
    { label: 'Terms & Conditions', href: '/terms-and-conditions/' },
    { label: 'Privacy Policy', href: '/privacy-policy/' },
  ],
  services: [
    { label: 'Our Care Process', href: '/your-care-planning-process/' },
    { label: 'Role of Carer', href: '/understanding-the-role-of-homecare-professionals/' },
    { label: 'Your Safety and Wellbeing', href: '/your-safety-and-wellbeing/' },
    { label: 'Support For Others', href: '/support-for-those-who-support-others/' },
    { label: 'Being There for You', href: '/being-there-for-you/' },
  ],
};

// Services shown on the homepage grid
export const services = [
  { title: 'Personal Care', slug: 'personal-care', blurb: 'Personal care services to help with daily tasks, ensuring comfort and dignity while promoting independence in the familiar surroundings of home.' },
  { title: 'Companionship at Home', slug: 'companionship', blurb: 'Our companionship services offer emotional support and meaningful activities to reduce loneliness, fostering connection and engagement with your loved ones.' },
  { title: 'Live-in Care', slug: 'live-in-care', blurb: 'Our live-in care option provides round-the-clock support, allowing your loved ones to stay in the comfort of their own home while receiving professional care.' },
  { title: 'Overnight Care', slug: 'overnight-care', blurb: 'Our carers stay awake during the night to provide reassurance and assistance while offering peace of mind to both clients and families.' },
  { title: 'Private Care at Home', slug: 'private-care', blurb: 'Tailored private care services to maintain your loved one’s independence and wellbeing, all while staying in the comfort and security of their own home.' },
  { title: 'Reablement Services', slug: 'reablement-services', blurb: 'Helping clients regain independence after illness or injury, our reablement services focus on improving daily living skills and building confidence at home.' },
  { title: 'Dementia Care', slug: 'dementia-and-alzheimer-care', blurb: 'Dementia care can cause distress for both patients and their families. We create an environment that reduces confusion and anxiety, allowing clients to maintain independence.' },
  { title: 'Palliative and End Of Life Care', slug: 'palliative-care', blurb: 'Palliative care can be emotionally challenging for everyone involved. We offer compassionate end-of-life support, ensuring you have the choice to remain in the comfort of your home.' },
  { title: 'Domiciliary Care', slug: 'domiciliary-care', blurb: 'If you’re struggling with daily tasks, we can help you stay safe and independent at home. We work closely with you to assess needs and manage risks.' },
];

// Secondary "even more options"
export const moreServices = [
  { title: 'Companionship', slug: 'companionship', blurb: 'Explore how we support our clients in visiting their friends, and arrangements.' },
  { title: 'Respite Care', slug: 'respite-care', blurb: 'Browse our team providing respite care for clients in their own homes.' },
];

// Homepage FAQ
export const homeFaqs = [
  { q: 'Is True Homecare Registered with the appropriate professional associations and bodies?', a: 'Yes. True Homecare is registered and regulated by the Care Quality Commission (CQC), the independent regulator of health and social care in England, and holds a “Good” rating.' },
  { q: 'How is the level of care to be provided assessed?', a: 'We begin with a free, no-obligation assessment. One of our care coordinators visits you at home to understand your needs, preferences and routines, then builds a tailored care plan around them.' },
  { q: 'What do you mean by a Customised, tailor-made care plan?', a: 'Every client is different. Your care plan is built specifically around your health needs, lifestyle and personal preferences — and is reviewed regularly so it adapts as your needs change.' },
  { q: 'What training do carers receive?', a: 'All of our carers are carefully selected, DBS-checked and trained to the highest standards, including specialist training for conditions such as dementia, Parkinson’s and palliative care.' },
  { q: 'What quality monitoring/assurance systems are in place?', a: 'We carry out regular reviews, spot checks and client feedback, and operate within the CQC’s regulatory framework to ensure consistently high-quality, safe care.' },
  { q: 'What tasks will my care worker carry out?', a: 'From personal care, medication support and meal preparation to companionship and help around the home — your care worker’s tasks are defined by your individual care plan.' },
];
