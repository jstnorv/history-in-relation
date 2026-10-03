# AI assistance: GitHub Copilot helped draft and refine this application.

import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, render_template, request


SOURCE_URL = "https://uhgi.org/"
SOURCE_NAME = "Ukrainian History Global Initiative, project overview"

TOPICS = [
    ("yamna", "Yamna", "Prehistory", "An Early Bronze Age steppe culture centered partly in present-day Ukraine, whose migrations are closely associated with the wider spread of Indo-European languages across Eurasia."),
    ("indo-european-languages", "Indo-European languages", "Language", "A language-family story that connects the lands of contemporary Ukraine with developments across a wider region."),
    ("scythia", "Scythia", "Antiquity", "A dynamic steppe world in the lands of contemporary Ukraine, connected through the Black Sea to the Bosporan Kingdom, Ancient Athens, and the wider classical world."),
    ("bosporan-kingdom", "Bosporan Kingdom", "Antiquity", "A polity around the Black Sea whose connections help frame the ancient history of the region."),
    ("ancient-athens", "Ancient Athens", "Antiquity", "Ancient Athens offers a Mediterranean lens on the lands of contemporary Ukraine, whose Black Sea connections with Scythia and the Bosporan Kingdom helped shape a shared classical-world frontier."),
    ("rus", "Rus", "Middle Ages", "A medieval polity centered on Kyiv, shaped by Slavic communities and by connections among Viking, Byzantine, Khazar, and western European worlds."),
    ("slavic-peoples", "Slavic peoples", "Middle Ages", "Diverse Slavic-speaking communities whose settlement, languages, and local political traditions formed a central foundation of Rus in the lands of contemporary Ukraine."),
    ("vikings", "Vikings", "Middle Ages", "Scandinavian traders, warriors, and settlers whose river networks linked Kyiv and Rus to the Baltic, the Black Sea, and Byzantium."),
    ("byzantium", "Byzantium", "Middle Ages", "A Black Sea and Christian-world connection that helped shape the political, religious, and cultural development of Rus in the lands of contemporary Ukraine."),
    ("khazars", "Khazars", "Middle Ages", "A powerful steppe empire whose trade networks, tributary relationships, and rivalry with Rus shaped the medieval world of the lands of contemporary Ukraine."),
    ("western-europe", "Western Europe", "Middle Ages", "The wider network of trade, diplomacy, dynastic marriage, and Christian exchange that connected Rus and Kyiv to medieval Europe."),
    ("cossacks", "Cossacks", "Early modern period", "A lens for exploring how the Cossacks defended autonomy and helped shape early forms of Ukrainian political community."),
    ("anti-colonial-or-proto-national-entities", "Anti-colonial or proto-national entities", "Historical theme", "A framework for examining communities that asserted autonomy and collective political identity before the age of modern nation-states."),
    ("soviet-union", "Soviet Union", "20th century", "The Soviet project made Ukraine central to its drive for industrialization, collectivized agriculture, and state-controlled social transformation—at immense human cost."),
    ("nazi-germany", "Nazi Germany", "20th century", "Nazi Germany regarded Ukraine as essential to its planned racial empire: a land to conquer, exploit for food and labor, and reshape through colonial settlement, deportation, and genocide."),
    ("global-transformation", "Global transformation", "20th century", "A lens for examining how Soviet and Nazi projects to remake the modern world made Ukraine a central arena of industry, agriculture, empire, war, and mass violence."),
    ("global-economy-and-politics", "Global economy and politics", "Modern history", "A framework for understanding how Ukraine’s history and the present war are shaped by—and help shape—global systems of trade, power, security, and international order."),
    ("russo-ukrainian-war", "Russo-Ukrainian war", "Modern history", "The project concludes with Russia’s ongoing war against Ukraine, confronting the invasion, occupation, civilian abuses, and attempted destruction of Ukrainian sovereignty while placing them in a longer history of imperial domination and Ukrainian resistance."),
]

CITATION_LINKS = {
    "nature+1": "https://www.nature.com/articles/s41586-024-08531-5",
    "nature+2": "https://www.nature.com/articles/s41586-024-08531-5",
    "science+1": "https://www.science.org/content/article/nomadic-herders-left-strong-genetic-mark-europeans-and-asians",
    "metmuseum": "https://www.metmuseum.org/",
    "cambridge+1": "https://www.cambridge.org/",
    "gaziakademikbakis": "https://gaziakademikbakis.com/",
    "encyclopediaofukraine": "https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CY%5CA%5CYamnaarcheologicalculturecomplex.htm",
    "encyclopediaofukraine+1": "https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CY%5CA%5CYamnaarcheologicalculturecomplex.htm",
    "doaks": "https://www.doaks.org/",
    "worldhistory+1": "https://worldhistory.org/",
    "search.worldcat+1": "https://search.worldcat.org/",
    "worldcat+1": "https://search.worldcat.org/",
    "husj.harvard+2": "https://www.husj.harvard.edu/",
    "encyclopedia.ushmm+1": "https://encyclopedia.ushmm.org/",
    "yadvashem+1": "https://www.yadvashem.org/",
    "pmc.ncbi.nlm.nih": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11909631/",
    "pmc.ncbi.nlm.nih+1": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11909631/",
    "lordslibrary.parliament+1": "https://lordslibrary.parliament.uk/",
}


def add_citation_links(text):
    if not text:
        return text

    pattern = re.compile(
        "|".join(
            re.escape(token) for token in sorted(CITATION_LINKS, key=len, reverse=True)
        )
    )

    def replace_token(match):
        token = match.group(0)
        url = CITATION_LINKS.get(token)
        if not url:
            return token
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{token}</a>'

    return pattern.sub(replace_token, text)


TOPIC_EXPLANATIONS = {
    "ancient-athens": """
    <h2>Ancient Athens and the northern Black Sea</h2>
    <p>Through the northern Black Sea, Ancient Athens was part of a wider network that linked the Greek world with Scythia, the Bosporan Kingdom, and the lands of contemporary Ukraine. Greek merchants, settlers, craftspeople, and political interests reached the region, where they encountered—and formed long-term relationships with—the peoples whom Greek authors called <strong>Scythians</strong>. Those interactions were not simply a story of Greek influence moving outward: they involved trade, diplomacy, artistic exchange, migration, and the development of shared cultural forms.</p>

    <h3>Connection to the Bosporan Kingdom</h3>
    <p>The <strong>Bosporan Kingdom</strong>, centered around Panticapaeum—present-day Kerch in Crimea—grew from Greek cities along the Cimmerian Bosporus into a Black Sea state that connected local communities, steppe populations, and the wider Greek world. Athens was an important destination for Bosporan grain, and the relationship tied the northern Black Sea economy to the food supply and political life of a major Greek city.</p>

    <p>This makes Ancient Athens more than a distant reference point. Through the Bosporan Kingdom, the region around Crimea participated in networks of shipping, agricultural exchange, material culture, and political recognition that stretched across the Black Sea and the Aegean. Bosporan society developed in contact with both Greek settlers and Scythian communities, making it a useful example of how the history of Ukraine’s southern lands intersects with classical Mediterranean history.</p>

    <h3>Connection to Scythia</h3>
    <p><strong>Scythia</strong> was the Greek name for a broad steppe world that included much of what is now Ukraine. Scythian peoples and Greek communities on the northern Black Sea coast lived alongside one another for centuries. Their contacts shaped trade, artistic styles, elite culture, and political relationships; archaeological and historical evidence points to strong Greek influences within parts of Scythian elite culture, while local traditions remained important.</p>

    <p>Athens was connected to this world indirectly through Black Sea trade and directly through Greek knowledge, representation, and encounters with Scythian people. The relationship should not be understood as a simple division between a “Greek” Athens and a separate “barbarian” Scythia. Rather, the northern Black Sea became a contact zone in which communities adapted foreign practices, maintained local identities, and produced cultural forms that cannot be reduced to either side alone.</p>

    <h3>Why this connection matters</h3>
    <p>Viewed together, <strong>Ancient Athens</strong>, the <strong>Bosporan Kingdom</strong>, and <strong>Scythia</strong> show that the lands of contemporary Ukraine were part of the classical world’s wider history. They were not merely a remote frontier of Greece, but a region where Mediterranean and steppe societies met and reshaped one another.</p>

    <p>Following these links helps explain why the history of Ukraine includes Black Sea maritime routes, Greek colonial cities, Scythian political and cultural traditions, and mixed Greco-Scythian forms of art and society. The connection is therefore not a claim that ancient Athens was Ukrainian; it is an invitation to see how the classical world was historically connected to places and peoples in and around present-day Ukraine.</p>
    """,
    "yamna": """
    <h2>Yamna</h2>
    <p><strong>Yamna</strong>—often called the Yamnaya or Pit Grave culture—was an Early Bronze Age archaeological complex of mobile and semi-mobile pastoralist communities that flourished on the Pontic-Caspian steppe from roughly 3300 to 2600 BCE. Its core zone included the grasslands and river valleys of present-day southern Ukraine, especially the lower Dnipro region, before expanding across a vast area from the Pannonian Basin in Central Europe to regions near the Altai Mountains.nature+1</p>

    <p>“Yamna” is an archaeological term, not the name of a known people, nation, or language. Archaeologists recognize the complex through shared material practices—especially burials in earthen mounds called <em>kurhans</em>, often with bodies laid in pits beneath them—along with evidence of herding, mobility, wagons, and exchange across the steppe. The communities associated with Yamna were diverse and changed over time; they should not be treated as direct equivalents of any modern population.encyclopediaofukraine+1</p>

    <h3>Ukraine’s prehistoric steppe</h3>
    <p>The lands of contemporary Ukraine were central to Yamna’s formation and early development. Recent archaeological and ancient-DNA research identifies the lower Dnipro–Don region as a key setting in which populations associated with earlier Serednii Stih communities interacted and contributed to the formation of Yamna groups. Mykhailivka, in today’s Kherson region, is among the important sites documenting this transition.nature+2</p>

    <p>This setting was a crossroads rather than a sealed birthplace. The North Pontic region connected farming communities to the west with hunter-gatherer and pastoralist societies from the wider Eurasian steppe. Mobility, livestock herding, river travel, and exchange linked populations across long distances, making the southern Ukrainian steppe part of a much larger prehistoric world.pmc.ncbi.nlm.nih</p>

    <h3>Connection to Indo-European languages</h3>
    <p>Yamna is closely associated with debates about the early spread of <strong>Indo-European languages</strong>. Ancient-DNA evidence demonstrates major population movements from the Pontic-Caspian steppe into parts of Europe during the third millennium BCE. These movements correspond broadly with linguistic models that connect steppe populations to the spread of several Indo-European language branches.science+1</p>

    <p>A 2025 genetic study proposes that the Dnipro–Don area, including present-day Ukraine, was the likely homeland of early Indo-European languages, while locating the deeper common Indo-Anatolian linguistic background farther east, in the North Caucasus–lower Volga region. These are active research conclusions, not final proof that any particular archaeological culture spoke a particular language.nature</p>

    <p>The careful formulation is that Yamna-associated expansions were likely <strong>one major pathway</strong> through which early Indo-European languages spread—not the entire explanation for every Indo-European-speaking community across Europe and Asia. Genetic ancestry, material culture, and language can move together, but they do not always do so.pmc.ncbi.nlm.nih+1</p>

    <h3>Why it matters</h3>
    <p>Yamna connects the deep history of Ukraine to transformations that affected much of Eurasia. The expansion of steppe pastoralist communities reshaped population patterns and helped create networks through which technologies, practices, and probably languages traveled across Europe and Asia.</p>

    <p>At the same time, this history should not be used to make modern nationalist or racial claims. Prehistoric populations did not possess modern national identities, and their movements do not determine who has political rights or cultural ownership today. The value of the Yamna connection is that it shows the lands of contemporary Ukraine as an active part of very long histories of migration, exchange, and linguistic change.</p>
    """,
    "indo-european-languages": """
    <h2>Indo-European languages</h2>
    <p><strong>Indo-European languages</strong> are a large family of related languages that includes Ukrainian and other Slavic languages, as well as Greek, Albanian, Armenian, the Romance and Germanic languages, Celtic languages, Indo-Iranian languages, and others. Linguists identify the family through shared patterns in vocabulary, grammar, and sound change—not because its speakers formed a single people, culture, or political community.</p>

    <p>The origin and early spread of these languages remain subjects of research and debate. One influential account, often called the <strong>steppe hypothesis</strong>, places an important stage of Proto-Indo-European development on the Pontic-Caspian steppe north of the Black and Caspian Seas, a region that includes parts of present-day Ukraine. Recent ancient-DNA research has strengthened the case for major population movements from this broader steppe region during the fourth and third millennia BCE, although genes, archaeological cultures, and languages cannot be treated as exact equivalents.nature+1</p>

    <h3>Connection to Yamna</h3>
    <p>The <strong>Yamna</strong> culture was an Early Bronze Age pastoralist culture that spread across the Pontic-Caspian steppe after roughly 3300 BCE. Its communities lived in a wide area that included parts of what are now Ukraine and Russia. Their mobility, use of wagons, herding economy, and burial practices make them central to discussions of prehistoric movement across Eurasia.nature+1</p>

    <p>Ancient-DNA studies show that people associated with Yamna contributed substantially to the ancestry of later populations in parts of Europe, particularly communities connected with the Corded Ware horizon in central and northern Europe. Because this expansion broadly overlaps with linguistic models for the spread of several Indo-European branches, researchers often associate Yamna movements with the wider dispersal of Indo-European languages.nature+1</p>

    <p>That association is a scholarly hypothesis, not a simple equation. Archaeological cultures are identified through material remains; genetic ancestry describes biological relationships; and language is learned and transmitted socially. People can adopt languages without large-scale migration, and migrants can adopt local languages. The strongest account therefore combines evidence from linguistics, archaeology, and genetics rather than treating any one kind of evidence as decisive on its own.science+1</p>

    <h3>Ukraine in a wider story</h3>
    <p>The lands of contemporary Ukraine matter to this history because the northern Black Sea and Dnipro steppe formed part of the landscape in which these prehistoric populations lived, interacted, and moved. New genomic research identifies a “Dnipro cline” among earlier populations in the region and argues that their interactions contributed to the formation of populations ancestral to Yamna communities.science+1</p>

    <p>This does <strong>not</strong> mean that modern Ukrainians are direct or exclusive inheritors of one prehistoric culture, nor that Ukraine can be reduced to an “origin point” for Europe. Over thousands of years, the region’s population, languages, borders, and identities changed repeatedly. The connection is valuable because it situates the lands of contemporary Ukraine within deep Eurasian histories of migration, exchange, and linguistic change.</p>

    <h3>Why it matters</h3>
    <p>Following Indo-European languages through the connection to Yamna expands the scale of Ukrainian history. It links the steppe north of the Black Sea to transformations that eventually affected communities from the Atlantic coast of Europe to South Asia.</p>

    <p>It also encourages careful historical thinking. Deep linguistic relationships do not establish modern political claims, ethnic purity, or timeless national identities. They show instead that the distant past of Ukraine, like the histories of language and population across Eurasia, was shaped by movement, mixture, and continuing cultural change.</p>
    """,
    "bosporan-kingdom": """
    <h2>Bosporan Kingdom</h2>
    <p>The <strong>Bosporan Kingdom</strong> was a Black Sea polity centered on the Cimmerian Bosporus, around the eastern Crimea and the Taman Peninsula. It developed from an alliance of Greek-founded cities and became a major point of contact between the Greek world, the Crimean Peninsula, and the steppe regions associated with present-day southern Ukraine. Its capital, Panticapaeum, stood at present-day Kerch.</p>

    <h3>A Black Sea crossroads</h3>
    <p>The kingdom helps show that the ancient history of the lands of contemporary Ukraine cannot be separated from the Black Sea. Its cities linked maritime routes, agricultural production, local populations, and long-distance exchange. Goods, people, artistic practices, and political ideas moved between the northern Black Sea coast and the wider Mediterranean through these networks.</p>

    <p>This was not simply a Greek colony at the edge of an otherwise separate world. Bosporan society developed in sustained contact with neighboring peoples, including Scythian communities. Archaeological evidence from the region reflects a cultural environment in which Hellenic and Scythian traditions met, changed, and at times combined. Panticapaeum itself became an important center for Scythian art, while artifacts from southern Ukraine and the Kuban show the work of both Hellenic and Scythian artisans.</p>

    <h3>Connection to Ancient Athens</h3>
    <p>The Bosporan Kingdom connected the northern Black Sea to <strong>Ancient Athens</strong> through trade, especially in grain and other agricultural goods. Athens depended on imported food supplies, and the Bosporan region became an important source of wheat for the Aegean world. This relationship placed the Black Sea economy—and the peoples and landscapes around it—within the material history of one of the best-known cities of classical Greece.</p>

    <p>The connection also helps shift the perspective from Athens alone to the routes, communities, and producers that made Mediterranean urban life possible. The lands around the northern Black Sea were participants in classical exchange networks, not merely distant settings described by Greek writers.</p>

    <h3>Connection to Scythia</h3>
    <p><strong>Scythia</strong> refers to the steppe world that included much of present-day southern Ukraine, where Scythian groups held power from roughly the seventh through the third centuries BCE. Relations between Scythian peoples and the Bosporan Kingdom included trade, cultural exchange, political rivalry, and conflict. Scythians later fought the kingdom and, at points, expanded their authority over other northern Black Sea states.</p>

    <p>Together, Scythia and the Bosporan Kingdom reveal a more connected ancient Black Sea region: coastal cities, steppe communities, local craftsmen, Greek-speaking settlers, and traveling merchants all helped shape its history. Their interaction also provides the link to Ancient Athens, whose economic and cultural world was connected to the northern Black Sea through the kingdom’s ports and trade routes.</p>
    """,
    "scythia": """
    <h2>Scythia</h2>
    <p><strong>Scythia</strong> was the name used by ancient Greek writers for the steppe region north of the Black Sea and for the peoples they identified as Scythians. In the history of the lands of contemporary Ukraine, Scythia refers especially to the mobile and politically influential communities that dominated much of the southern steppe from roughly the seventh through the third centuries BCE. Their world extended beyond modern Ukraine, but the grasslands, river valleys, Black Sea coast, and Crimea were central to its history.metmuseum</p>

    <p>Scythia was not a single, unified state or a timeless ethnic homeland. It was a changing world of pastoralists, farmers, warriors, traders, and regional leaders. Greek accounts are indispensable but partial: they describe Scythian peoples through Greek assumptions and interests. Archaeology—including burial mounds, settlements, weapons, horse equipment, and goldwork—helps recover evidence of Scythian life and their relationships with neighboring societies.</p>

    <h3>A Black Sea contact zone</h3>
    <p>The northern Black Sea was a contact zone where Scythian communities encountered Greek-founded cities from at least the seventh century BCE. These coastal settlements became points of exchange between the Mediterranean, the Black Sea, and the steppe. Scythians supplied products such as grain, livestock, hides, and furs; Greek traders brought wine, olive oil, ceramics, metal goods, and other crafted objects.cambridge+1</p>

    <p>This did not produce a simple story of Greek culture replacing local traditions. Scythian and Greek communities influenced one another over centuries through trade, diplomacy, intermarriage, conflict, and artistic exchange. Scythian goldwork, for example, combined established steppe animal styles with Greek motifs and techniques, creating forms that were neither wholly Greek nor wholly separate from the wider classical world.metmuseum</p>

    <h3>Connection to Ancient Athens</h3>
    <p><strong>Ancient Athens</strong> was linked to Scythia through the broader economy of the Black Sea. Athenian demand for grain tied the city to producers and ports in the northern Black Sea region, while merchants, sailors, artisans, and travelers carried goods and knowledge between the Aegean and the steppe. Athens also employed Scythian archers in public policing, an example of how people from the Black Sea world could become part of life in a major Greek city.gaziakademikbakis</p>

    <p>This relationship places the lands of contemporary Ukraine within classical history without describing them as a passive eastern margin of Greece. Scythian communities shaped the commercial conditions, political relationships, and cultural encounters that made northern Black Sea trade possible. Greek cities depended on those relationships; Scythian elites and communities, in turn, engaged selectively with a world that extended far beyond the steppe.</p>

    <h3>Connection to the Bosporan Kingdom</h3>
    <p>The <strong>Bosporan Kingdom</strong> emerged around the Kerch Strait, connecting Crimea and the Taman Peninsula through Greek-founded cities and Black Sea trade. Its rulers, urban communities, and merchants interacted closely with Scythian groups in Crimea and the surrounding steppe. The kingdom’s economy depended on agricultural production and exchange with the populations beyond its cities, while its material culture reflects long-term Greco-Scythian interaction.metmuseum</p>

    <p>Relations included negotiation, trade, alliance, and conflict. By the late second century BCE, Scythian political expansion in Crimea placed the Bosporan Kingdom under severe pressure. The two should therefore not be treated as sealed-off societies: the Scythian steppe and Bosporan coastal cities formed an interconnected northern Black Sea world with overlapping economies, contested territory, and blended cultural practices.metmuseum</p>

    <h3>Why it matters</h3>
    <p>Scythia shows that the lands of contemporary Ukraine were connected to ancient Mediterranean and Eurasian history through the Black Sea long before the formation of medieval states. It also complicates modern national narratives: Scythian peoples were ancient steppe communities, not direct equivalents of any modern nation.</p>

    <p>Following Scythia’s links to Athens and the Bosporan Kingdom highlights the project’s central idea—history becomes clearer in relation. The ancient history of Ukraine’s southern lands developed through movement, exchange, and conflict among peoples whose worlds crossed the Black Sea, the steppe, and the Mediterranean.</p>
    """,
    "slavic-peoples": """
    <h2>Slavic peoples</h2>
    <p><strong>Slavic peoples</strong> refers to diverse communities connected by related languages and cultural histories, not to one unchanging or unified people. In the early medieval period, Slavic-speaking groups lived across a broad area of central, eastern, and southeastern Europe. The communities most relevant to the history of contemporary Ukraine lived along the Dnipro, Dniester, Southern Buh, and other river systems, where they developed distinct local identities, economies, and political relationships.encyclopediaofukraine+1</p>

    <p>By the early Middle Ages, groups such as the Polianians, Siverianians, Derevlianians, Volhynians, Ulychians, and Tivertsi lived in territories that now form part of Ukraine. They were connected by related languages and some shared cultural practices, but they were not a modern Ukrainian nation, nor were they politically uniform. Their communities made alliances, paid tribute, fought rivals, and adapted to relationships with steppe powers, neighboring peoples, and expanding states.encyclopediaofukraine+1</p>

    <h3>Connection to Rus</h3>
    <p><strong>Rus</strong> emerged among and incorporated many Slavic-speaking communities. Slavic agricultural settlements, river routes, local elites, tribute systems, and social structures formed much of the population base and material foundation of the medieval polity centered on Kyiv. The Polianians, who lived around Kyiv, held a particularly important place in accounts of Rus’s early formation.encyclopediaofukraine</p>

    <p>Slavic influence should not be confused with an exclusive Slavic origin. Rus also developed through Scandinavian military and commercial networks, trade and diplomacy with Byzantium, rivalry and exchange with the Khazars and other steppe powers, and connections with western and central Europe. Slavic communities were central participants in this process, but Rus was shaped by multiple peoples and long-distance relationships.encyclopediaofukraine+1</p>

    <h3>Language, identity, and change</h3>
    <p>Language gives historians one way to trace relationships among these communities, but it cannot by itself define political loyalty or modern national identity. The East Slavic languages from which Ukrainian, Belarusian, and Russian later developed were shaped gradually over centuries, through regional variation, migration, literary traditions, state formation, and contact with neighboring languages.</p>

    <p>It is therefore misleading to project modern national categories directly back onto the early medieval period. The history of Slavic peoples in Ukraine is not evidence that one modern state or nation “owns” Rus. Rather, it helps explain the deep historical connections among the peoples of eastern Europe while recognizing that each community’s history developed differently over time.encyclopediaofukraine+1</p>

    <h3>Why it matters</h3>
    <p>Slavic communities are essential to the history of Ukraine because they formed much of the social and linguistic landscape in which Rus developed. Their relationship to Rus helps explain the foundations of settlement, agriculture, local political authority, and language in the Dnipro region.</p>

    <p>At the same time, studying them in relation to Vikings, Byzantium, Khazars, and western Europe keeps the story accurate. The medieval history of the lands of contemporary Ukraine was created through exchange, conflict, migration, and political adaptation—not through a single isolated origin.</p>
    """,
    "vikings": """
    <h2>Vikings</h2>
    <p><strong>Vikings</strong> were Scandinavian seafarers, traders, warriors, settlers, and political actors active across Europe and beyond between roughly the eighth and eleventh centuries. In the eastern European context, they are often called <strong>Varangians</strong>. Their connection to the lands of contemporary Ukraine ran through river routes linking Scandinavia and the Baltic to the Dnipro, the Black Sea, and Constantinople.encyclopediaofukraine+1</p>

    <p>This was not simply a story of Viking raids arriving from the north. Varangians traveled through—and at times settled in—an already populated landscape of Slavic communities, steppe powers, trading towns, and river networks. They exchanged goods, served as mercenaries, formed alliances, and participated in early political structures. Over time, many became part of the multilingual, multiethnic society of Rus rather than remaining a separate Scandinavian community.encyclopediaofukraine</p>

    <h3>The route to Kyiv</h3>
    <p>The best-known connection is the <strong>Varangian route</strong>, often called the route “from the Varangians to the Greeks.” It ran from Scandinavia through waterways and portages into the Dnipro system, then south through the lands of contemporary Ukraine to the Black Sea and Constantinople. The route covered nearly 3,000 kilometers and became important from the ninth century onward.encyclopediaofukraine</p>

    <p>Kyiv occupied a strategic position on this network. Goods such as furs, wax, honey, timber, silver, textiles, wine, and luxury objects moved along related routes, while control of river crossings, tribute systems, and fortified settlements could generate wealth and political power. The Dnipro also posed dangers: travelers faced rapids, difficult portages, and attacks from steppe groups.worldhistory+1</p>

    <h3>Connection to Rus</h3>
    <p><strong>Rus</strong> developed through the interaction of Varangian networks with Slavic communities and the political geography of the steppe and Black Sea. Scandinavian-linked groups participated in trade, warfare, and early rulership, while local Slavic-speaking populations made up much of the society, agricultural base, and territorial landscape of the expanding polity. The term <em>Rus</em> itself is commonly associated with early Scandinavian groups, though the medieval polity that came to bear the name was far more than a Viking creation.encyclopediaofukraine+1</p>

    <p>Varangians held administrative and military roles under Rus princes and served as mercenaries for Byzantine emperors. Their participation connected Kyiv not only to Scandinavia but also to Byzantine commercial and diplomatic networks. These connections helped Rus become a major medieval political center, but its institutions and culture emerged through local adaptation and exchange—not through the simple transfer of a Scandinavian model.encyclopediaofukraine</p>

    <h3>Why it matters</h3>
    <p>The Viking connection places medieval Ukraine within a large network that joined northern Europe to the Black Sea and eastern Mediterranean. It explains why Kyiv became a major center of trade and political power, while also showing how state formation grew from the interaction of many peoples.</p>

    <p>Calling Vikings one element in the formation of Rus does not make Rus “foreign,” nor does it diminish the importance of Slavic communities in its history. It highlights a more accurate picture: the medieval lands of contemporary Ukraine were a crossroads where Scandinavian mobility, Slavic settlement, Byzantine influence, Khazar power, and steppe politics intersected.</p>
    """,
    "byzantium": """
    <h2>Byzantium</h2>
    <p><strong>Byzantium</strong>, the eastern continuation of the Roman Empire, was one of the most important external influences on the medieval history of the lands of contemporary Ukraine. Its power extended across the eastern Mediterranean and Black Sea, while the Dnipro River connected Kyiv and other Rus centers to Byzantine ports, markets, and the imperial capital of Constantinople.</p>

    <p>The relationship was never only cultural or religious. It involved trade, diplomacy, military conflict, treaty-making, and dynastic politics. Rus rulers and merchants travelled south along the Dnipro toward the Black Sea and Constantinople, carrying goods such as furs, wax, honey, and enslaved people; in return, they encountered commodities and cultural influences circulating through the Byzantine world.</p>

    <h3>Connection to Rus</h3>
    <p>The relationship between <strong>Byzantium</strong> and <strong>Rus</strong> was central to the formation of the medieval political and cultural world centered on Kyiv. Early encounters included warfare and negotiation: after a Rus campaign against Constantinople in 907, a trade agreement in 911 laid the foundations for more permanent relations between the two powers.</p>

    <p>In 988, during the rule of Volodymyr, Rus adopted Christianity in the Byzantine rite. This decision connected the lands of Rus more closely to the Orthodox Christian world and helped reinforce political unity within the realm. It also introduced and adapted Byzantine traditions of religious life, architecture, art, law, literacy, and learning.</p>

    <h3>A Ukrainian connection</h3>
    <p>Byzantine influence did not erase local traditions or turn Rus into a copy of Constantinople. The culture of Rus developed through the interaction of Slavic communities, Scandinavian networks, steppe societies, and Byzantine Christianity. Kyiv was a political and commercial center within that connected world, rather than a distant recipient of ideas from the south.</p>

    <p>The connection matters for the history of Ukraine because Byzantine Christianity helped shape institutions and cultural traditions that remained important in Ukrainian lands for centuries. Churches, monastic communities, artistic forms, written learning, and political ideas all developed locally through engagement with a broader Byzantine Christian sphere.</p>

    <h3>Why it matters</h3>
    <p>Studying Byzantium alongside Rus places medieval Ukraine within a Black Sea and eastern European network of movement and exchange. The Dnipro was not only a local river: it formed part of a major route linking the Baltic and Black Seas, Scandinavia and Byzantium, and Kyiv with the wider Christian world.</p>

    <p>This perspective avoids treating the history of Rus as the exclusive origin story of any one modern nation. Instead, it highlights the medieval connections that shaped the lands of contemporary Ukraine and influenced the cultural inheritance shared, interpreted, and contested by different communities over time.</p>
    """,
    "khazars": """
    <h2>Khazars</h2>
    <p>The <strong>Khazars</strong> were a Turkic-speaking people who built a powerful khaganate between the seventh and tenth centuries. At its height, the Khazar realm extended across parts of the northern Caucasus, the Sea of Azov steppe, Crimea, and the eastern European steppe, reaching toward the Dnipro River. This placed it directly within the historical geography of present-day eastern and southern Ukraine.encyclopediaofukraine</p>

    <p>Khazaria was not simply a steppe empire defined by warfare. It was also a commercial and political crossroads. Its rulers collected tribute, taxed goods moving through their territory, and helped control routes linking the Byzantine Empire, the Islamic world, the Caucasus, the Volga basin, Scandinavia, and Slavic-speaking communities farther north and west. The Khazar capital, Itil, became an important East–West trading center.brill+1</p>

    <h3>A connected medieval world</h3>
    <p>The Khazar presence challenges any account of medieval Ukraine that begins only with Slavic settlement or the emergence of Rus. In the early medieval centuries, the steppe and river systems around the Black Sea connected many peoples: Khazars, Slavic communities, Bulgars, Alans, Vikings or Varangians, Byzantine officials and merchants, and traders from the Islamic world.</p>

    <p>Political power moved across this landscape through alliances, military campaigns, marriage ties, tribute, and trade. Several eastern Slavic communities—including the Polianians and Siverians, who lived in areas associated with the history of Ukraine—paid tribute to the Khazars.encyclopediaofukraine</p>

    <h3>Connection to Rus</h3>
    <p><strong>Rus</strong> emerged within a political and commercial landscape that the Khazars had helped shape. Before the consolidation of Rus around Kyiv, Khazar power influenced trade routes and local systems of tribute across the Dnipro basin and nearby steppe. Rus merchants and raiders also moved through Khazar-controlled territory toward the Volga, Black Sea, and Caspian regions, bringing the two powers into both contact and competition.msutexas.contentdm.oclc+1</p>

    <p>The relationship changed over time. As Rus rulers expanded their authority, they challenged Khazar control over territory and routes. In 964–65, Prince Sviatoslav of Kyiv defeated major Khazar centers, including Itil and Semender, while Rus annexed Sarkil and parts of Khazar territory. This contributed to the destruction of the Khazar state as a regional power.encyclopediaofukraine</p>

    <h3>Why it matters</h3>
    <p>Placing the Khazars alongside Rus shows that the formation of medieval political communities in the lands of contemporary Ukraine occurred through interaction, not isolation. Khazar authority, commercial networks, and conflicts formed part of the environment in which Rus developed.</p>

    <p>The Khazar connection should not be understood as a claim that Rus was simply “Khazar,” or that one people directly produced the other. Rather, it highlights a wider medieval world in which Ukraine’s steppe and river regions connected societies across Europe, the Black Sea, the Caucasus, and western Asia.</p>
    """,
    "western-europe": """
    <h2>Western Europe</h2>
    <p><strong>Western Europe</strong> was one part of the wider medieval world connected to the lands of contemporary Ukraine. The term includes the Latin-Christian kingdoms and principalities of regions such as Poland, Hungary, Scandinavia, France, and the Holy Roman Empire—not a single unified political or cultural bloc. Rus interacted with these societies through trade, dynastic marriage, diplomacy, warfare, pilgrimage, and religious exchange.compass.onlinelibrary.wiley+1</p>

    <p>These ties challenge the idea that medieval Ukraine stood outside “Europe” or was isolated on its eastern edge. Kyiv and other Rus centers participated in networks that crossed the Baltic, Central Europe, and the Black Sea. The medieval world was not divided into sealed eastern and western civilizations; it was made up of overlapping routes, families, markets, religious traditions, and political relationships.</p>

    <h3>Connection to Rus</h3>
    <p><strong>Rus</strong> maintained extensive connections with western and central European courts. Dynastic marriages were particularly important. Rulers of Rus arranged marriages with members of ruling families in Poland, Hungary, Norway, Sweden, Denmark, France, and the Holy Roman Empire, using kinship to build alliances, establish status, support diplomacy, and widen commercial relationships. Research on the ruling dynasty of Rus finds that roughly 70 percent of its external dynastic marriages formed ties with western European polities.huri.harvard</p>

    <p>One well-known example is <strong>Anna Yaroslavna of Kyiv</strong>, daughter of Yaroslav the Wise. In 1051, she married King Henry I of France and became queen of France; after Henry’s death, she served as co-regent during the minority of their son, Philip I. Her life demonstrates that connections between Kyiv and western Europe were not abstract or indirect—they operated through people who held political authority at the highest levels of medieval society.doaks</p>

    <h3>Exchange across Europe</h3>
    <p>Dynastic connections supported more than royal family histories. They created channels for diplomatic envoys, religious contacts, material culture, and political information. Trade linked the Dnipro basin with markets in Central Europe and the Baltic, while the movement of clergy, manuscripts, travelers, and artisans connected Rus to wider European Christian cultures.</p>

    <p>These relationships did not eliminate important differences. Rus entered the Christian world principally through Byzantine Christianity, while much of western Europe was organized around Latin Christianity. The growing institutional separation between the Orthodox and Catholic churches made the distinction increasingly consequential after the eleventh century. Yet shared Christian practices, family ties, political needs, and commercial interests continued to produce contact across that divide.search.worldcat+1</p>

    <h3>Why it matters</h3>
    <p>The western European connection places Rus within medieval Europe without reducing its history to a western model. Kyiv was connected both to Latin-Christian courts in the west and to Byzantium, the Black Sea, the Islamic world, Scandinavia, and the steppe.</p>

    <p>Studying these connections helps correct two distortions: treating the lands of contemporary Ukraine as a marginal space outside Europe, and treating Rus as the exclusive inheritance of one modern country. Medieval Rus was a connected political world centered for key periods on Kyiv, formed through relationships that reached in many directions.</p>
    """,
    "rus": """
    <h2>Rus</h2>
    <p><strong>Rus</strong> was a medieval political world centered for much of its history on Kyiv and the Dnipro river system. It developed from the ninth century through the interaction of local Slavic communities, Scandinavian trading and military networks, Byzantine Christianity and diplomacy, Khazar political and commercial power, and contacts with western and central Europe. The familiar term “Kyivan Rus” is modern, but it usefully distinguishes this medieval polity from later states that have claimed parts of its legacy.husj.harvard+1</p>

    <p>For the history of contemporary Ukraine, Rus is important not as a simple national beginning, but as a connected medieval formation. Kyiv was a major center in a network that linked the Baltic to the Black Sea and Constantinople, the steppe to forest regions, and eastern Europe to wider Christian, Islamic, and Eurasian worlds. Its institutions and culture developed through these relationships rather than from a single people or a self-contained territory.husj.harvard+1</p>

    <h3>Slavic foundations</h3>
    <p><strong>Slavic peoples</strong> formed the largest part of the population in the regions from which Rus emerged. Their languages, agricultural communities, local social structures, and political relationships were foundational to the development of towns, principalities, and the wider cultural landscape of Rus.</p>

    <p>“Slavic” should not be mistaken for one unified medieval nation. The Slavic-speaking communities of the Dnipro basin and neighboring regions were diverse, with different local identities, leaders, alliances, and experiences. Rus brought many of these communities into changing forms of political relationship, sometimes through agreement and tribute, and sometimes through conquest.worldhistory</p>

    <h3>Vikings, Byzantium, and Khazars</h3>
    <p><strong>Vikings</strong>, often called Varangians in eastern European sources, linked Rus to Scandinavian and Baltic networks. Scandinavian groups participated in trading, raiding, military service, and dynastic rule, but they worked within—and soon intermarried with—predominantly Slavic societies. The growth of Kyiv as a political center was closely connected to the control of routes between the Baltic and Black Seas.worldhistory</p>

    <p><strong>Byzantium</strong> connected Rus to the eastern Mediterranean through diplomacy, trade, warfare, and Christianity. Rus rulers negotiated commercial agreements with Constantinople and, in 988, Volodymyr adopted Christianity in the Byzantine rite. This decision helped create religious, literary, artistic, and institutional traditions that developed locally in the lands of contemporary Ukraine.britannica+1</p>

    <p>The <strong>Khazars</strong> formed another essential part of Rus’s early environment. Their khaganate influenced tributary systems, commercial routes, and political relationships across the steppe and river regions. As Rus expanded, it inherited, competed for, and eventually challenged parts of the connected landscape that Khazar power had helped organize.encyclopediaofukraine</p>

    <h3>Western European links</h3>
    <p><strong>Western Europe</strong> was also part of Rus’s medieval horizon. Dynastic marriages connected Rus ruling families to royal and princely houses in Scandinavia, Poland, Hungary, France, and the Holy Roman Empire. Trade, pilgrimage, diplomacy, and religious exchange created further links. Rather than a boundary separating Rus from “Europe,” the continent’s western and eastern regions were connected through overlapping networks of people, goods, and political relationships.husj.harvard+1</p>

    <h3>Why it matters</h3>
    <p>Understanding Rus as a synthesis avoids two misleading extremes: the claim that it was the exclusive origin of one modern nation, and the claim that its history can be detached from the lands of contemporary Ukraine. Rus was a multi-regional and multilingual medieval polity whose center of gravity was, for key periods, Kyiv and the Dnipro basin.</p>

    <p>Its legacy is shared and contested. Modern Ukrainians, Belarusians, and Russians all relate to aspects of Rus’s history, but none can fully own it. A relation-focused approach instead asks how Slavic communities, Vikings, Byzantium, Khazars, and western Europe helped make Rus—and how Rus, in turn, shaped the medieval history of the lands that are now Ukraine.</p>
    """,
    "cossacks": """
    <h2>Cossacks</h2>
    <p>The <strong>Cossacks</strong> matter in this project because they help expand the story of Ukraine beyond the medieval and early modern categories often used in simpler national narratives. The Cossack world emerged in a landscape of steppe politics, military mobility, and layered cultural identities, where communities developed forms of political life shaped by local traditions, military practice, and interaction with neighboring powers.</p>

    <h3>Connection to anti-colonial or proto-national entities</h3>
    <p>The Cossacks are presented here as an early example of an <strong>anti-colonial or proto-national entity</strong>. That framing does not reduce the Cossacks to a modern nationalist model, but it does help explain why they are often treated as a historical expression of collective political identity emerging from the conditions of borderlands, military conflict, and state competition.</p>

    <p>In the lands of contemporary Ukraine, this matters because it draws attention to the ways communities developed political and cultural forms in response to pressures from outside powers, from imperial rivalry, and from the realities of life on the frontier. The Cossacks therefore represent not only a military formation but a political imagination that helped shape later understandings of collective belonging.</p>
    """,
    "anti-colonial-or-proto-national-entities": """
    <h2>Anti-colonial or proto-national entities</h2>
    <p><strong>Anti-colonial or proto-national entities</strong> is a historical lens for examining communities that defended political autonomy, developed collective institutions, or articulated a shared political homeland before the rise of modern nationalism. It does not mean that early modern people held the same national ideas as people do today. Instead, it helps identify earlier forms of self-government, political loyalty, and resistance that later generations could connect to Ukrainian national history.</p>

    <p>In the lands of contemporary Ukraine, the <strong>Cossacks</strong> provide an important example. From the late fifteenth century onward, Cossack communities emerged in the Dnipro borderlands, organizing military forces and forms of self-rule in a region shaped by the competing power of the Polish-Lithuanian Commonwealth, the Crimean Khanate, the Ottoman Empire, and Muscovy.</p>

    <h3>Why “proto-national”?</h3>
    <p>“Proto-national” signals an important qualification. The Cossack political world was not a modern nation-state, and Cossack identity did not include everyone who lived in the territory of present-day Ukraine. Cossack communities were socially diverse, politically divided, and embedded in wider imperial and regional systems.</p>

    <p>Yet the Cossack Hetmanate created institutions that gave political form to a distinct Ukrainian territory and population: a military organization, administration, courts, fiscal practices, and an elected—or at least formally elective—hetman. Cossack elites also developed the idea of a Ukrainian political homeland on both banks of the Dnipro, well before nineteenth-century mass nationalism.</p>

    <h3>Connection to the Cossacks</h3>
    <p>The Cossacks illustrate the “anti-colonial” part of the theme because they repeatedly sought to protect or expand their liberties against larger states. Before the uprising led by Bohdan Khmelnytsky, Cossacks had limited self-rule within the Polish-Lithuanian Commonwealth. The Cossack-Polish War that began in 1648 led to the formation of the Cossack Hetmanate, a polity that governed substantial parts of central and northeastern Ukraine.</p>

    <p>Its autonomy, however, remained contested. The Hetmanate navigated relationships with Poland-Lithuania, Muscovy, the Ottoman Empire, and the Crimean Khanate rather than operating outside imperial power altogether. After the Pereiaslav agreement of 1654, it existed as an autonomous polity within Muscovy, but Russian authorities progressively limited its independent institutions. The Russian government abolished the office of hetman in 1764, and destroyed the Zaporozhian Sich in 1775.</p>

    <h3>Why it matters</h3>
    <p>The Cossack experience should not be simplified into an uninterrupted march toward a modern Ukrainian state. Its history includes alliances, internal conflicts, unequal social relations, and changing political goals. Still, the Cossacks left a durable legacy: institutions of autonomy, memories of political freedom, and a language of rights and liberties that later Ukrainian movements drew upon.</p>

    <p>The theme therefore connects Ukraine’s modern national history to an earlier struggle over who could govern the Dnipro lands, organize armed power, administer local life, and define a political community amid competing empires.</p>
    """,
    "soviet-union": """
    <h2>Soviet Union</h2>
    <p>The <strong>Soviet Union</strong> treated Ukraine as indispensable to its project of remaking society through centralized rule, industrialization, collectivized agriculture, and political control. Ukraine’s coal and steel regions, agricultural production, transportation networks, and population made it one of the USSR’s most important republics. Yet Soviet rule was not simply a story of economic development: it also brought the destruction of political independence, repression of Ukrainian cultural and intellectual life, forced collectivization, famine, deportation, and terror.</p>

    <p>Ukraine was not a passive setting for Soviet policy. Ukrainians worked, studied, created, resisted, accommodated, and organized under Soviet rule. But the Soviet state exercised decisive power over land, food, labor, political expression, and national institutions—often through coercion and violence. Understanding the Soviet Union in Ukraine therefore requires holding modernization and repression together, rather than presenting industrial achievement as a substitute for the human cost of Soviet rule.encyclopediaofukraine+1</p>

    <h3>Collectivization and the Holodomor</h3>
    <p>In the late 1920s and early 1930s, Joseph Stalin’s government forced peasants into collective farms, seized agricultural property, imposed grain quotas, and punished communities that failed to meet state demands. Ukraine’s agricultural output was central to Soviet plans to finance rapid industrialization, but those policies stripped rural households of food and undermined their ability to survive.encyclopediaofukraine+1</p>

    <p>The result was the <strong>Holodomor</strong>, the man-made famine of 1932–33 in Soviet Ukraine. Millions of people died. Soviet authorities confiscated grain and other food, enforced punitive measures against villages and farms, restricted movement, and blocked many starving people from seeking food elsewhere. The famine was accompanied by a broader assault on Ukrainian cultural, political, and intellectual life.husj.harvard+2</p>

    <p>Scholars debate particular questions of intent, classification, and death toll, but there is no serious basis for treating the Holodomor as a natural disaster. It resulted from Soviet policies and state actions. Many states and institutions recognize it as genocide against the Ukrainian people; others use terms such as man-made famine or famine-genocide while emphasizing the same central facts of coercion, mass death, and political repression.lordslibrary.parliament+1</p>

    <h3>Connection to global transformation</h3>
    <p>The Soviet Union framed itself as a revolutionary experiment with global ambitions. Its leaders sought to create a new social and economic order through state planning, mass industrial development, collective agriculture, and ideological education. Ukraine was one of the central territories on which that transformation was attempted.</p>

    <p>Its industrial regions supplied coal, steel, machinery, and labor; its farms were expected to provision cities and support exports; and its people were subjected to policies intended to produce a disciplined Soviet society. The Holodomor exposes the violence embedded in that project: state planners and security institutions treated food, land, and human life as resources to be mobilized for a larger political goal.encyclopediaofukraine+1</p>

    <h3>Repression and legacy</h3>
    <p>Soviet power in Ukraine also relied on surveillance, censorship, arrest, execution, deportation, and the suppression of independent political life. The Great Terror of the 1930s brought imprisonment, exile, and death to vast numbers of people, including Ukrainian writers, artists, scholars, clergy, officials, and ordinary citizens. These campaigns severely damaged the institutions and cultural networks through which Ukrainians could sustain public and political life.encyclopediaofukraine+1</p>

    <p>Placing the Soviet Union within <strong>global transformation</strong> does not minimize Ukrainian agency or reduce Ukraine to an object of history. It clarifies how a state claiming to build a universal future made Ukraine central to its economic ambitions—and how that same project inflicted catastrophic suffering. The Soviet experience remains essential for understanding Ukrainian historical memory, the value placed on sovereignty, and the continuing resistance to Russian imperial claims over Ukraine.</p>
    """,
    "nazi-germany": """
    <h2>Nazi Germany</h2>
    <p><strong>Nazi Germany</strong> placed Ukraine at the center of its plans to conquer and reorder eastern Europe. Nazi leaders viewed Ukrainian lands not as the homeland of a sovereign people, but as territory to seize for agricultural production, military control, German settlement, and racial empire. This vision joined economic exploitation to a hierarchy that denied equal human value and political rights to Jews, Roma, Slavs, and other populations targeted by the regime.encyclopedia.ushmm+1</p>

    <p>Germany invaded the Soviet Union on 22 June 1941, and by the end of that year nearly all of present-day Ukraine was under Nazi occupation. The occupation divided Ukrainian territory into separate administrative zones, each governed according to German military, colonial, or allied priorities. Rather than support meaningful Ukrainian independence, Nazi authorities imposed coercive rule, extracted resources, and violently suppressed political, cultural, and civilian life.yadvashem+1</p>

    <h3>Occupation and exploitation</h3>
    <p>Ukraine’s agricultural capacity was central to Nazi plans. Under the idea of <em>Lebensraum</em>—“living space”—Nazi leaders imagined an eastern empire that would provide land and food for Germans while subordinating, displacing, exploiting, or killing those they categorized as racially inferior. <strong>Generalplan Ost</strong> paired long-term colonization with demographic engineering, including mass deportation, enslavement, and starvation.encyclopedia.ushmm+1</p>

    <p>Occupation authorities requisitioned food, raw materials, and labor for the German war effort. Their policies helped create acute deprivation and hunger among civilians. Millions of people from Ukraine were deported or compelled to work for Nazi Germany; forced labor was integral to the wartime economy and was imposed through violence, discriminatory racial policy, and denial of basic rights.encyclopedia.ushmm+1</p>

    <h3>Genocide in Ukraine</h3>
    <p>Nazi occupation brought the Holocaust to Ukraine. German forces, SS units, police formations, and local collaborators murdered Jewish people in ghettos, camps, forests, ravines, and other sites across the country. Many victims were shot close to the towns and cities where they had lived—what scholars commonly call the “Holocaust by bullets.”ushmm</p>

    <p>Nazi persecution also targeted Roma people, Soviet prisoners of war, disabled people, political opponents, and civilians accused of resistance. The occupation’s violence cannot be separated from its economic and colonial aims: racial ideology justified the theft of resources, forced labor, displacement, and mass murder.encyclopedia.ushmm+1</p>

    <h3>Connection to global transformation</h3>
    <p>Nazi Germany provides a devastating example of <strong>global transformation</strong> carried out through conquest. Its leaders sought to reshape the population, economy, and geography of eastern Europe on a continental scale. Ukraine was central to this project because Nazi plans treated it as both a source of food and labor and a future zone of German colonial settlement.encyclopedia.ushmm+1</p>

    <p>The Nazi project was not simply an external episode in Ukrainian history. It reshaped Ukrainian society through occupation, forced movement, collaboration, resistance, loss, and the destruction of Jewish communal life. Studying it alongside the Soviet Union shows how Ukraine became a major site where competing twentieth-century visions of empire, modernization, racial order, and political power inflicted catastrophic human consequences.</p>
    """,
    "global-transformation": """
    <h2>Global transformation</h2>
    <p><strong>Global transformation</strong> is a lens for understanding how twentieth-century efforts to remake economies, societies, territories, and populations were experienced in Ukraine. Ukraine was not peripheral to these projects: its agricultural output, industrial regions, transportation routes, strategic location, and diverse population made its lands central to the ambitions of both the Soviet Union and Nazi Germany.</p>

    <p>The term does not suggest that transformation was neutral or inevitable. In Ukraine, programs presented as modernization, revolution, empire-building, or national renewal often depended on coercion, dispossession, forced labor, mass violence, and the destruction of communities. Ukraine’s twentieth-century history shows how large ideological visions became realities in particular places and in people’s daily lives.</p>

    <h3>Connection to the Soviet Union</h3>
    <p>The <strong>Soviet Union</strong> presented itself as a revolutionary project that would transform society through industrialization, collectivized agriculture, and centralized planning. Ukraine was fundamental to those ambitions. Its coal and steel regions, especially the Donbas, were important to Soviet industrial development, while its agricultural production made it central to state plans for food supply and grain exports.</p>

    <p>Under Stalin’s First Five-Year Plan, forced collectivization gave the Soviet state control over much of Ukraine’s agricultural production. In 1932–33, state policies—including coercive grain requisitions and the confiscation of food—produced the Holodomor, a man-made famine in which millions of Ukrainians died. The tragedy demonstrates the human cost of treating land, labor, and food as resources to be controlled for an accelerated state project.</p>

    <h3>Connection to Nazi Germany</h3>
    <p><strong>Nazi Germany</strong> envisioned an even more openly racial and colonial remaking of eastern Europe. In Nazi plans for <em>Lebensraum</em>—“living space”—Ukraine was to be conquered, exploited, and transformed into a source of food, land, labor, and settlement for a German empire. These ambitions joined economic extraction to racial hierarchy and genocidal policy.</p>

    <p>After Germany invaded the Soviet Union in June 1941, most of Ukraine came under German occupation. Nazi authorities seized food and resources for the German war effort, deported roughly 2.2 million people from Ukraine for forced labor in Germany, and carried out the Holocaust. At least 1.5 million Jews were murdered in Ukraine, with many killed near their homes by German forces and their collaborators.</p>

    <h3>A site of collision</h3>
    <p>The Soviet and Nazi projects were distinct and should not be collapsed into one story: they differed in ideology, institutions, goals, and the forms of power they used. Yet both treated Ukraine as crucial to a far-reaching redesign of Europe and the world. Soviet authorities sought to mobilize Ukraine’s people and resources for a centrally planned socialist transformation; Nazi authorities sought colonial domination, racial reordering, extraction, and extermination.</p>

    <p>Placing the <strong>Soviet Union</strong> and <strong>Nazi Germany</strong> in relation therefore makes Ukraine’s centrality visible. Ukrainian lands became a site where rival visions of economy, empire, race, labor, territory, and political order brought catastrophic consequences. The history also resists narratives that treat Ukraine only as a setting for other powers: Ukrainians, including workers, peasants, intellectuals, soldiers, victims, resisters, and collaborators, experienced and responded to these transformations under extreme conditions.</p>

    <h3>Why it matters</h3>
    <p>This theme connects Ukraine’s twentieth-century history to global questions: How do states use modernization to expand control? How can economic planning and imperial ambition make ordinary people vulnerable? What happens when racial ideology turns territory and populations into objects of conquest?</p>

    <p>Studying global transformation through Ukraine makes clear that modernity was not simply a story of progress. It was also shaped by authoritarian rule, colonial ambition, famine, forced migration, war, and genocide—and Ukraine was one of the places where those processes were concentrated most intensely.</p>
    """,
    "global-economy-and-politics": """
    <h2>Global economy and politics</h2>
    <p><strong>Global economy and politics</strong> is a framework for understanding how events in Ukraine are shaped by—and in turn reshape—systems beyond its borders. Ukraine’s territory has long connected the Black Sea, Central and Eastern Europe, and Eurasia through agricultural production, trade routes, migration, imperial competition, and military strategy. In the modern era, its significance also includes energy transit, industrial capacity, access to the Black Sea, and major exports of grain, maize, sunflower oil, and other commodities.</p>

    <p>This perspective does not treat Ukraine as merely a location where outside powers act. Ukrainians, Ukrainian institutions, and Ukraine’s economy have been active parts of wider political and commercial networks. Questions of sovereignty, security, trade access, and control over infrastructure have had consequences both within Ukraine and far beyond it.</p>

    <h3>Connection to the Russo-Ukrainian war</h3>
    <p>The <strong>Russo-Ukrainian war</strong> is a struggle over Ukraine’s sovereignty and territorial integrity, but it also has global economic and political effects. Russia’s full-scale invasion disrupted commodity markets, trade routes, finance, energy supplies, and food systems. Before the full-scale invasion, Russia and Ukraine together accounted for about one-quarter of global wheat exports, making disruptions in the Black Sea region especially consequential for food-importing countries.</p>

    <p>The war has also demonstrated the importance of Ukraine’s Black Sea ports and agricultural infrastructure. When conflict restricts shipping or damages storage, transport, and production capacity, the effects reach consumers and producers well beyond Europe. The United Nations helped establish arrangements intended to facilitate grain and food exports from Ukrainian ports; after the Black Sea Grain Initiative ended in July 2023, the UN continued to emphasize the importance of maintaining food and fertilizer flows to global markets.</p>

    <h3>Food, energy, and security</h3>
    <p>The war’s economic effects are closely linked. Disruptions to Ukrainian grain exports can increase food prices and deepen food insecurity, particularly in lower-income importing countries. At the same time, disruptions involving Russian energy supplies and commodity exports have affected global fuel prices, inflation, industrial production, and government budgets.</p>

    <p>These impacts do not mean that Ukraine’s value should be measured only in grain, energy infrastructure, or strategic geography. Rather, they show how violence directed at Ukraine can affect interconnected systems on which people in many countries depend. The World Bank described the invasion’s consequences as far-reaching both for Ukrainians and for the wider world, including through food prices and their impact on poorer households.</p>

    <h3>A longer history</h3>
    <p>Connecting the present war to global economy and politics also makes its longer historical context visible. Ukraine’s lands have repeatedly been drawn into contests among larger powers because of their location, productive capacity, river and sea routes, and connections between European, Black Sea, and Eurasian regions. But geography does not determine history on its own: political decisions, institutions, social movements, and the choices of people living in Ukraine have shaped how these connections developed.</p>

    <p>The central lesson is that the war should neither be treated as an isolated regional crisis nor reduced to an abstract contest among great powers. It is a war against Ukraine that has global implications—affecting international law, alliances, trade, food security, energy markets, and the future of the rules meant to protect state sovereignty.</p>
    """,
    "russo-ukrainian-war": """
    <h2>Russo-Ukrainian war</h2>
    <p>The <strong>Russo-Ukrainian war</strong> is the most recent chapter in a longer history of political, economic, and cultural entanglement. This project does not treat it as a sudden rupture from nowhere. Instead, it connects the war to earlier patterns of state formation, imperial conflict, migration, and the long history of the lands of contemporary Ukraine within larger geopolitical systems.</p>

    <h3>Connection to global economy and politics</h3>
    <p>The war is deeply tied to <strong>global economy and politics</strong>. It is shaped by geopolitics, energy systems, military strategy, and the broader structure of post-Cold War order. Understanding the war requires seeing it within international relationships as well as within the long local histories that preceded it.</p>

    <p>That is why these pages keep returning to the longer story: the present war is not disconnected from earlier periods of movement, conflict, and interdependence. It is one modern expression of a region whose history has long been shaped by interaction with broader worlds.</p>
    """,
}

CONNECTIONS = [
    ("yamna", "indo-european-languages", "Associated with the spread of", "UHGI highlights the role of the Yamna in the spread of what would become Indo-European languages."),
    ("scythia", "bosporan-kingdom", "Connected with", "UHGI treats Scythia and the Bosporan Kingdom together as part of the ancient history of the region."),
    ("bosporan-kingdom", "ancient-athens", "Synthesized with", "UHGI describes a synthesis of Scythia and the Bosporan Kingdom with ancient Athens in the development of classical culture."),
    ("scythia", "ancient-athens", "Part of a cultural synthesis with", "UHGI describes a synthesis of Scythia and the Bosporan Kingdom with ancient Athens in the development of classical culture."),
    ("rus", "slavic-peoples", "Formation included", "UHGI describes Rus as a unique medieval state with Slavic elements."),
    ("rus", "vikings", "Formation included", "UHGI describes Rus as a unique medieval state with Viking elements."),
    ("rus", "byzantium", "Formation included", "UHGI describes Rus as a unique medieval state with Byzantine elements."),
    ("rus", "khazars", "Formation included", "UHGI describes Rus as a unique medieval state with Khazar elements."),
    ("rus", "western-europe", "Formation included", "UHGI describes Rus as a unique medieval state with western European elements."),
    ("cossacks", "anti-colonial-or-proto-national-entities", "Presented as an early example of", "UHGI describes the Cossacks as an early anti-colonial or proto-national entity."),
    ("soviet-union", "global-transformation", "A perspective on", "UHGI discusses Ukraine's centrality to Soviet views of global transformation."),
    ("nazi-germany", "global-transformation", "A perspective on", "UHGI discusses Ukraine's centrality to Nazi views of global transformation."),
    ("russo-ukrainian-war", "global-economy-and-politics", "Considered in a wider context of", "A framework for understanding how Ukraine’s history and the present war are shaped by—and help shape—global systems of trade, power, security, and international order."),
]


def get_seed_version():
    payload = {
        "topics": TOPICS,
        "connections": CONNECTIONS,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def init_db(database_path):
    """Create the schema and refresh the seeded graph when the source data changes."""
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                period TEXT NOT NULL,
                summary TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY,
                from_topic_id INTEGER NOT NULL REFERENCES topics(id),
                to_topic_id INTEGER NOT NULL REFERENCES topics(id),
                relationship TEXT NOT NULL,
                explanation TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_name TEXT NOT NULL,
                UNIQUE (from_topic_id, to_topic_id, relationship)
            );
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        seed_version = get_seed_version()
        stored_seed = connection.execute(
            "SELECT value FROM app_settings WHERE key = 'seed_version'"
        ).fetchone()

        if stored_seed is None or stored_seed[0] != seed_version:
            connection.execute("DELETE FROM connections")
            connection.execute("DELETE FROM topics")
            connection.executemany(
                "INSERT INTO topics (slug, name, period, summary) VALUES (?, ?, ?, ?)",
                TOPICS,
            )
            topic_ids = dict(
                connection.execute("SELECT slug, id FROM topics").fetchall()
            )
            connection.executemany(
                """
                INSERT INTO connections
                    (from_topic_id, to_topic_id, relationship, explanation, source_url, source_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        topic_ids[source],
                        topic_ids[target],
                        relationship,
                        explanation,
                        SOURCE_URL,
                        SOURCE_NAME,
                    )
                    for source, target, relationship, explanation in CONNECTIONS
                ],
            )
            connection.execute(
                "INSERT INTO app_settings (key, value) VALUES ('seed_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (seed_version,),
            )

        connection.commit()
    finally:
        connection.close()


def format_related_list(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def build_topic_context(topic_name, connections):
    if not connections:
        return f"{topic_name} is not yet linked to any other topic."

    related_names = []
    seen_names = set()
    relationship_summaries = []

    for connection in connections:
        related_name = connection["related_name"]
        if related_name == topic_name:
            continue
        if related_name not in seen_names:
            related_names.append(related_name)
            seen_names.add(related_name)

        relationship_summaries.append(
            f"{connection['relationship']} {related_name}: {connection['explanation']}"
        )

    related_text = format_related_list(related_names)
    summary = f"{topic_name} is connected to {related_text}."
    if relationship_summaries:
        summary += " " + " ".join(relationship_summaries)
    return summary


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "UHGI_DATABASE", str(Path(__file__).with_name("connections.sqlite3"))
        )
    )
    if test_config:
        app.config.update(test_config)
    init_db(app.config["DATABASE"])

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        database = g.pop("db", None)
        if database is not None:
            database.close()

    @app.get("/")
    def index():
        search = request.args.get("q", "").strip()
        database = get_db()
        if search:
            like = f"%{search}%"
            topics = database.execute(
                """
                SELECT * FROM topics
                WHERE name LIKE ? OR period LIKE ? OR summary LIKE ?
                ORDER BY id
                """,
                (like, like, like),
            ).fetchall()
        else:
            topics = database.execute(
                "SELECT * FROM topics ORDER BY id"
            ).fetchall()
        connection_count = database.execute(
            "SELECT COUNT(*) FROM connections"
        ).fetchone()[0]
        return render_template(
            "index.html",
            topics=topics,
            search=search,
            connection_count=connection_count,
        )

    @app.get("/topic/<slug>")
    def topic_detail(slug):
        database = get_db()
        topic = database.execute(
            "SELECT * FROM topics WHERE slug = ?", (slug,)
        ).fetchone()
        if topic is None:
            abort(404)
        connections = database.execute(
            """
            SELECT
                c.relationship,
                c.explanation,
                c.source_url,
                c.source_name,
                CASE WHEN c.from_topic_id = ? THEN target.name ELSE source.name END AS related_name,
                CASE WHEN c.from_topic_id = ? THEN target.slug ELSE source.slug END AS related_slug
            FROM connections AS c
            JOIN topics AS source ON source.id = c.from_topic_id
            JOIN topics AS target ON target.id = c.to_topic_id
            WHERE c.from_topic_id = ? OR c.to_topic_id = ?
            ORDER BY related_name, c.relationship
            """,
            (topic["id"], topic["id"], topic["id"], topic["id"]),
        ).fetchall()
        topic_context = build_topic_context(topic["name"], connections)
        topic_explanation = add_citation_links(TOPIC_EXPLANATIONS.get(slug, ""))
        return render_template(
            "topic.html",
            topic=topic,
            connections=connections,
            topic_context=topic_context,
            topic_explanation=topic_explanation,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
