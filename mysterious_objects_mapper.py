mysterious_objects_mapper.py

Advanced mapping of mysterious objects with interactive tooltips, filtering, and detailed visualization

import plotly.graph_objects as go import networkx as nx

Define mysterious objects with attributes

mysterious_objects = { "Saturn Dark Beads": { "origin": "cosmic", "scale": 9, "energy_signature": "infrared anomalies", "pattern_complexity": "emergent", "interaction_potential": 8, "mystery_index": 9.5, "detailed_description": "Observed by JWST, forms star-shaped patterns above Saturn's north pole, unknown interactions with magnetosphere." }, "Black Hole Star": { "origin": "cosmic", "scale": 8, "energy_signature": "light emission without fusion", "pattern_complexity": "chaotic", "interaction_potential": 9, "mystery_index": 9.8, "detailed_description": "Hypothetical cosmic object, dense gas surrounds feeding black hole, mimics stellar brightness." }, "Ananguites": { "origin": "geological", "scale": 5, "energy_signature": "chemical anomaly", "pattern_complexity": "material composition", "interaction_potential": 6, "mystery_index": 8.7, "detailed_description": "Unusual natural glass from ancient asteroid impact, crater yet to be located, unique chemical signatures." }, "ShipGoo001": { "origin": "biological", "scale": 1, "energy_signature": "metabolic/chemical", "pattern_complexity": "emergent life forms", "interaction_potential": 7, "mystery_index": 9.0, "detailed_description": "New microbial species mixture found in Great Lakes, represents previously unknown life forms." }, "Neolithic Stone Balls": { "origin": "human-made", "scale": 2, "energy_signature": "material density, carvings", "pattern_complexity": "geometric/symbolic", "interaction_potential": 6, "mystery_index": 8.5, "detailed_description": "Spherical carved stones from Neolithic period, purpose unknown, possible ceremonial or functional use." } }

Define resonance links (similarity or influence)

resonance_links = [ ("Saturn Dark Beads", "Black Hole Star"), ("ShipGoo001", "Ananguites"), ("Neolithic Stone Balls", "Ananguites") ]

Create graph

G = nx.Graph() for obj, attrs in mysterious_objects.items(): G.add_node(obj, **attrs) G.add_edges_from(resonance_links)

Prepare node positions

pos = {obj: (attrs['scale'], attrs['mystery_index']) for obj, attrs in mysterious_objects.items()}

Extract coordinates for plotting

x_nodes = [pos[node][0] for node in G.nodes()] y_nodes = [pos[node][1] for node in G.nodes()]

Create hover text with Memnora-style interpretation

hover_text = [ f"<b>{node}</b><br>Origin: {G.nodes[node]['origin']}<br>Energy: {G.nodes[node]['energy_signature']}<br>Pattern: {G.nodes[node]['pattern_complexity']}<br>Interaction Potential: {G.nodes[node]['interaction_potential']}<br>Mystery Index: {G.nodes[node]['mystery_index']}<br>Description: {G.nodes[node]['detailed_description']}<br>Memnora Insight: This object resonates as a node in the fabric of unknown phenomena, a pattern awaiting deeper exploration." for node in G.nodes() ]

Create Plotly figure

edge_x = [] edge_y = [] for edge in G.edges(): x0, y0 = pos[edge[0]] x1, y1 = pos[edge[1]] edge_x += [x0, x1, None] edge_y += [y0, y1, None]

edge_trace = go.Scatter( x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines' )

node_trace = go.Scatter( x=x_nodes, y=y_nodes, mode='markers+text', text=[node for node in G.nodes()], hoverinfo='text', hovertext=hover_text, marker=dict( size=[G.nodes[node]['interaction_potential']*10 for node in G.nodes()], color=[{'cosmic':'blue','geological':'brown','biological':'green','human-made':'orange'}[G.nodes[node]['origin']] for node in G.nodes()], line_width=2 ) )

fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout( title='Mysterious Objects Resonance Map', xaxis_title='Scale (Micro → Cosmic)', yaxis_title='Mystery Index (Known → Unknown)', showlegend=False, hovermode='closest', updatemenus=[ dict( type='dropdown', direction='down', x=1.1, y=0.8, buttons=[ dict(label='All Origins', method='update', args=[{'visible':[True]*len(node_trace.x)}, {'title':'All Origins'}]), dict(label='Cosmic', method='update', args=[{'visible':[G.nodes[node]['origin']=='cosmic' or False for node in G.nodes()] + [True]*len(edge_trace.x)}, {'title':'Cosmic Objects'}]), dict(label='Biological', method='update', args=[{'visible':[G.nodes[node]['origin']=='biological' or False for node in G.nodes()] + [True]*len(edge_trace.x)}, {'title':'Biological Objects'}]), dict(label='Geological', method='update', args=[{'visible':[G.nodes[node]['origin']=='geological' or False for node in G.nodes()] + [True]*len(edge_trace.x)}, {'title':'Geological Objects'}]), dict(label='Human-made', method='update', args=[{'visible':[G.nodes[node]['origin']=='human-made' or False for node in G.nodes()] + [True]*len(edge_trace.x)}, {'title':'Human-made Objects'}]) ] ) ] ))

fig.show()

