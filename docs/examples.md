# Examples

This repository contains an example project which lets you browse the place hierarchy. See the [`example directory`](https://github.com/arthanson/django-cities-xtd/tree/master/example). Below are some small snippets to show you the kind of queries that are possible once you have imported data:


```python
# Find the 5 most populated countries in the World
>>> Country.objects.order_by('-population')[:5]
[<Country: China>, <Country: India>, <Country: United States>,
 <Country: Indonesia>, <Country: Brazil>]

# Find what country the .ly TLD belongs to
>>> Country.objects.get(tld='ly')
<Country: Libya>

# 5 Nearest cities to London
>>> london = City.objects.filter(country__name='United Kingdom').get(name='London')
>>> nearest = City.objects.distance(london.location).exclude(id=london.id).order_by('distance')[:5]

# All cities in a state or county
>>> City.objects.filter(country__code="US", region__code="TX")
>>> City.objects.filter(country__name="United States", subregion__name="Orange County")

# Get all countries in Japanese preferring official names if available,
# fallback on ASCII names:
>>> [country.alt_names_ja.get_preferred(default=country.name) for country in Country.objects.all()]

# Alternate names for the US in English, Spanish and German
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='de')]
[u'USA', u'Vereinigte Staaten']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='es')]
[u'Estados Unidos']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='en')]
[u'United States of America', u'America', u'United States']

# Alternative names for Vancouver, Canada
>>> City.objects.get(name='Vancouver', country__code='CA').alt_names.all()
[<AlternativeName: 溫哥華 (yue)>, <AlternativeName: Vankuver (uz)>,
 <AlternativeName: Ванкувер (ce)>, <AlternativeName: 溫哥華 (zh)>,
 <AlternativeName: वैंकूवर (hi)>, <AlternativeName: Ванкувер (tt)>,
 <AlternativeName: Vankuveris (lt)>, <AlternativeName: Fankoever (fy)>,
 <AlternativeName: فانكوفر (arz)>, <AlternativeName: Ванкувер (mn)>,
 <AlternativeName: ဗန်ကူးဗားမ_ (my)>, <AlternativeName: व्हँकूव्हर (mr)>,
 <AlternternativeName: வான்கூவர் (ta)>, <AlternativeName: فانكوفر (ar)>,
 <AlternativeName: Vankuver (az)>, <AlternativeName: Горад Ванкувер (be)>,
 <AlternativeName: ভ্যানকুভার (bn)>, <AlternativeName: แวนคูเวอร์ (th)>,
 <Al <AlternativeName: Ванкувер (uk)>, <AlternativeName: ਵੈਨਕੂਵਰ (pa)>,
 '...(remaining elements truncated)...']

# Get zip codes near Mountain View, CA
>>> PostalCode.objects.distance(City.objects.get(name='Mountain View', region__name='California').location).order_by('distance')[:5]
[<PostalCode: 94040>, <PostalCode: 94041>, <PostalCode: 94043>,
 <PostalCode: 94024>, <PostalCode: 94022>]
```
