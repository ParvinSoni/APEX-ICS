import matplotlib.pyplot as plt
import numpy as np

protocols = ['Modbus/TCP', 'IEC-104', 'Ethernet/IP (Non-ConMgr)', 'BachMann/3500', 'DNP3', 'CodeSys v3.0', 'Ethernet/IP (ConMgr)']

# Define the actual numbers of key fields. 
ground_truth_key_fields = {'Modbus/TCP': 3, 'IEC-104': 9, 'Ethernet/IP (Non-ConMgr)': 7, 'BachMann/3500': 2, 'DNP3': 3, 'CodeSys v3.0': 2, 'Ethernet/IP (ConMgr)': 3}

# Define the identified numbers of key field by fraemworks.  
found_key_fields = {'Netzob': {'Modbus/TCP': 3, 'IEC-104': 1, 'Ethernet/IP (Non-ConMgr)': 2, 'BachMann/3500':0, 'DNP3': 2, 'CodeSys v3.0': 6, 'Ethernet/IP (ConMgr)': 13},
                    'NetPlier': {'Modbus/TCP': 3, 'IEC-104': 6, 'Ethernet/IP (Non-ConMgr)': 4, 'BachMann/3500':0, 'DNP3': 0, 'CodeSys v3.0': 5, 'Ethernet/IP (ConMgr)': 5},
                    'APEX-ICS': {'Modbus/TCP': 3, 'IEC-104': 9, 'Ethernet/IP (Non-ConMgr)': 1, 'BachMann/3500':2, 'DNP3': 3, 'CodeSys v3.0': 2, 'Ethernet/IP (ConMgr)': 4}}

n_groups = len(protocols)
index = np.arange(n_groups)
bar_width = 0.15
opacity = 0.70

for i, framework in enumerate(found_key_fields.keys()):
    r2 = index + i * bar_width
    plt.bar(r2, [ground_truth_key_fields[p] for p in protocols], width=bar_width, alpha=opacity, color='black', label='Ground Truth')
    plt.bar(r2 + bar_width, np.array([found_key_fields[framework][p] for p in protocols]), width=bar_width, alpha=opacity, label=framework)

#plt.xticks(r1, protocols, fontsize=8)

plt.xticks(index + bar_width, protocols, rotation=45, fontsize=8)
plt.ylabel('Number of Key Fields')
plt.legend()

plt.tight_layout()
plt.show()
