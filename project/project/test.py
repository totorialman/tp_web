from graphviz import Digraph

traceroute_with_latency = {
    "bmstu.ru": [
        ("10.0.2.2", 10.589), ("10.221.72.81", 38.380), ("10.221.74.64", 39.603),
        ("10.221.76.66", 38.879), ("95.167.95.10", 39.496), ("57.core3.sto.he.net", 49.135),
        ("195.19.50.250", 52.009)
    ],
    "www.iana.org": [
        ("10.0.2.2", 40.353), ("10.221.72.81", 40.353), ("10.221.74.64", 41.526),
        ("10.221.76.66", 41.638), ("95.167.95.10", 44.147), ("57.core3.sto.he.net", 53.733),
        ("185.140.149.151", 53.733), ("192.0.32.8", 208.703)
    ],
    "www.jp-australia.com": [
        ("10.0.2.2", 0.334), ("10.221.72.81", 47.003), ("10.221.74.64", 46.911),
        ("10.221.76.66", 46.893), ("ae204-99.dataix.eu", 56.749), ("core3.sto.he.net", 65.645),
        ("core3.ash.he.net", 76.705), ("core3.fra.he.net", 75.029), ("core3.muc.he.net", 75.054),
        ("core3.zrh.he.net", 75.063), ("core3.mil.he.net", 75.129), ("core3.syd.he.net", 75.033),
        ("83.171.237.9", 75.033)
    ]
}

dot_latency_clean = Digraph(comment="Traceroute Visualization with Latencies (Clean)")

for destination, hops in traceroute_with_latency.items():
    for i in range(len(hops) - 1):
        src, _ = hops[i]  
        dst, dst_latency = hops[i + 1]  
        dot_latency_clean.node(src, src)
        dot_latency_clean.node(dst, dst)
        dot_latency_clean.edge(src, dst, label=f"{dst_latency} ms")

output_path_clean_latency = "C:/Users/main/Desktop/code/tp_web/tp_web"
dot_latency_clean.render(output_path_clean_latency, format="png", cleanup=True)
output_path_clean_latency + ".png"