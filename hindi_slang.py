"""Contextual Hindi/Hinglish hints, paraphrased rather than copied definitions.

References checked 2026-11-07:
https://www.urbandictionary.com/define.php?term=dalle
https://www.urbandictionary.com/define.php?term=Dalla
https://www.urbandictionary.com/define.php?term=Bakchodi
https://www.urbandictionary.com/define.php?term=E-Lafda
https://www.urbandictionary.com/define.php?term=Nalla
https://www.urbandictionary.com/define.php?term=Chapri
https://blog.karlrock.com/list-of-common-hindi-swear-words/

These are contextual translation hints, not an exhaustive dictionary or a blocklist.
Never infer real criminal conduct, a person's caste or a family relationship from abuse.
"""

EXTRA_SLANG_HINTS = [
    (r'\bdall(?:a|e|ey|on)?\b|\bdalaa?l\b|दल्ला|दल्ले|दलाल',
     'dalla/dalle/dalal: pimp literally; an insulting address, or sellout/lackey in context. Dalal can also mean a neutral broker/agent. Do not invent trafficking. DALL-E is an AI product, not abuse.'),
    (r'\bbha?d(?:wa|va|ua|we|ve|ue|wo|vo)\b|भड़व[ाे]',
     'bhadwa/bhadve/bhadua: pimp or a contemptuous vulgar insult such as bastard; preserve the intended insult rather than inventing a literal occupation.'),
    (r'\b(?:hara+m(?:i|za+da|ja+da|za+de|ja+de)|hara+m[kx]hor)\b|हरामी|हरामखोर|हरामज़ाद',
     'harami/haramzada: bastard, scoundrel, sometimes cheeky rascal in banter. Haramkhor: freeloader/scoundrel; distinguish anger from joking.'),
    (r'\b(?:kameen[aei]|kamin[aei])\b|कमीना|कमीने|कमीनी',
     'kameena/kamina/kameeni: bastard, nasty person or a playful rascal. Match tone; do not add gendered abuse absent from the original.'),
    (r'\b(?:sa+la|sa+le|sa+li|saa?ley)\b|साला|साले|साली',
     'saala/saale/saali: often a casual insult or intensifier, but literal brother/sister-in-law in family context; not always a severe sexual insult.'),
    (r'\b(?:rand[iy]|raand|randi(?:baaz|rona|pana)|randirona)\b|रंडी|रांड',
     'randi/raand: whore/slut as abuse, not proof of sex work. Randirona: bitching/whining. Randibaaz: womanizer in context.'),
    (r'\b(?:nall[aei]|nikamm[aei]|vell[aei])\b|नल्ला|नल्ले|निकम्मा|वेल्ला',
     'nalla/nikamma: useless bum, good-for-nothing or idle person. Vella: free/idle, not automatically abusive. Nalla can mean good in South Indian languages; use language context.'),
    (r'\b(?:fatt[uio]|fattu)\b|फट्टू|फत्तू',
     'fattu: coward/chicken/scaredy-cat; not a sexual insult.'),
    (r'\b(?:jh?aa?t[uio]|jhant[uio])\b|झाटू|झाँटू',
     'jhatu/jhaatu: contemptible idiot/loser, derived from pubic-hair slang; usually not literal hair in an insult.'),
    (r'\b(?:thark[iy]|hawas[iy])\b|ठरकी|हवसी',
     'tharki: horny/pervy; hawasi: lustful/lecherous. Do not turn a crude joke into an allegation of assault.'),
    (r'\b(?:chha?pr[iy]|chapr[iy])\b|छपरी|छप्री',
     'chapri/chhapri: derogatory tacky wannabe or cringe showoff in internet slang. Do not invent a caste, class or ethnic identity.'),
    (r'\b(?:bew?d[aeiy]|bevd[aeiy]|charsi|ganjed[iy]|nashed[iy])\b|बेवड़ा|बेवड़े|चरसी|गंजेड़ी|नशेड़ी',
     'bewda/bevda: drunkard; charsi/ganjedi/nashedi: stoner/druggie in slang. It may be teasing; do not present it as a medical fact.'),
    (r'\b(?:bew?a?koof|bevakoof|bevkoof|bevkuf|bewkuf)\b|बेवकूफ',
     'bewakoof/bevkoof: fool/stupid, generally milder than chutiya; do not upgrade it to severe profanity.'),
    (r'\b(?:gadh[aei]|ull[uio]|ullu\s+ka\s+pattha)\b|गधा|गधे|उल्लू',
     'gadha/ullu/ullu ka pattha: fool/idiot when insulting someone; donkey/owl literally in an animal context.'),
    (r'\b(?:kutt[aeiy]|sua+r|suwa+r)\b|कुत्ता|कुत्ते|कुतिया|सूअर',
     'kutta/kutte: dog or a dog-like insult; kutiya: bitch; suar: pig. Distinguish pets and actual animals from abuse.'),
    (r'\baand(?:u|on)?\b|\btatt(?:a|e|ey|i)\b|आंड|टट्टे|टट्टी',
     'aand/tatte: balls/testicles; tatti: shit/crap. The English conjunction and is not aand. Do not mix tatti with tatte.'),
    (r'\b(?:choot|chut|bhosd[ai])\b|चूत|भोसड़ा',
     'choot/chut/bhosda: vulgar genital slang (cunt/pussy); chut can be shorthand but chhut/chhoot can mean leave, discount or exemption.'),
    (r'\b(?:muth|mooth|hilaa?|hila\s+raha|mutth)\b|मुठ|मूठ',
     'muth/mooth: masturbation in sexual slang; hila can mean shake or jerk off depending on context. Do not sexualize an ordinary movement.'),
    (r'\b(?:moot|mut(?:na|ne)|pesha?b|pisha?b)\b|मूत|पेशाब',
     'moot/mutna/peshab: piss/pee depending on register; moot diya can be figurative dominance or contempt, not necessarily literal urination.'),
    (r'\b(?:hag(?:na|ne|gu|ga)?|hugg?|goo|gu)\b|हग|गू',
     'hagna/hag diya: shit or figuratively mess up badly/do a shitty job; haggu: someone doing a terrible job. Use the sentence’s meaning.'),
    (r'\bl[ao]u?d[ae]\s+lag|\b(?:chud|chudi)\s+gay|लौड़े लग|चुद गई|चुद गए',
     'lode/laude lag gaye, chud gaye: we/I are fucked, screwed or in deep shit; typically figurative trouble, not a literal sexual event.'),
    (r'\b(?:ga+nd\s+(?:faa?d|phaa?d|phat)|gandfat|gandfut)\b|गांड फाड़|गांड फट',
     'gaand phatna: scared shitless or overwhelmed; gaand faad: amazing/intense in praise, or tear someone a new one in an actual insult.'),
    (r'\b(?:bhak|bhaag|chal\s+be|abe|abey|oye|oyee)\b|अबे|ओए|भक',
     'abe/abey/oye: hey/oi, rude or friendly depending on the relationship. Bhak/chal be: get lost/oh piss off in dismissal; do not add hostility to friendly calls.'),
    (r'\b(?:bakwa+s|bakwaas|bakar|bkc|bakaiti)\b|बकवास|बकैती',
     'bakwaas: nonsense/bullshit; bakar/bakaiti: idle chatter or talking crap. Choose strength from context.'),
    (r'\b(?:lafd[ae]|laphd[ae]|bhasad|bawa+l|bawal|panga|kalesh|ka+nd)\b|लफड़ा|भसड़|बवाल|पंगा|कलेश|कांड',
     'lafda/bhasad/bawaal/panga/kalesh: trouble, fight, drama or a mess; kaand: incident/scandal/antics. Not always a physical fight or crime.'),
    (r'\b(?:chamch[aei]|chatukaar|chaa?tu|talw[ae]\s+chaa?t)\b|चमचा|चमचे|चाटुकार',
     'chamcha/chaatu: suck-up, bootlicker or sycophant; chamcha literally means spoon when discussing utensils.'),
    (r'\b(?:juga+a?d|scene|set\s+hai|setting|jhol|jugaad)\b|जुगाड़|झोल',
     'jugaad: workaround/resourceful arrangement; scene: situation/plan/vibe; jhol: something fishy/a complication. Setting need not mean romance or corruption.'),
    (r'\b(?:ghant[ae]|ghantaa|ghanta)\b|घंटा|घंटे',
     'ghanta: hour/bell literally, but dismissive yeah right/as if/fuck all in slang. Read the whole sentence.'),
    (r'\b(?:jhaka+s|jhakkas|kadak|faadu|fadu|mast|zabardast)\b|झकास|कड़क|फाड़ू|मस्त',
     'jhakaas/kadak/faadu/mast/zabardast: awesome/brilliant or intense praise; kadak also means strong/crisp literally.'),
    (r'\b(?:besharam|behaya|ghatiya|badtameez|badtamiz)\b|बेशर्म|बेहया|घटिया|बदतमीज़',
     'besharam/behaya: shameless; ghatiya: lousy/despicable; badtameez: rude/ill-mannered. Do not automatically make these sexual insults.'),
    (r'\b(?:laund[aeiy]|lound[aeiy]|laundiya)\b|लौंडा|लौंडे|लौंडिया',
     'launda/launde: boy/guys in colloquial speech; laundiya: girl, often disrespectful. Distinct from lauda (dick).'),
    (r'\b(?:patli\s+gali|kat\s+le|nikal\s+le|bhag\s+yahan)\b|पतली गली|कट ले|निकल ले',
     'patli gali se nikal/kat le: slip away/get out of here; literal narrow lanes only when actually giving directions.'),
]
