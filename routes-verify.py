import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

subscription_id = "$AZURE_SUBSCRIPTION_ID"
resource_group_aks = "$RESOURCE_GROUP_AKS"
resource_group_appgw = "$RESOURCE_GROUP_APPGW"
name_route_table_aks = "$NAME_ROUTE_TABLE_AKS"
name_route_table_appgw = "$NAME_ROUTE_TABLE_APPGW"

credential = DefaultAzureCredential()

network_client_aks = NetworkManagementClient(credential, subscription_id)
network_client_appgw = NetworkManagementClient(credential, subscription_id)

route_table_aks = network_client_aks.route_tables.get(resource_group_aks, name_route_table_aks)
routes_aks = route_table_aks.routes

route_table_appgw = network_client_appgw.route_tables.get(resource_group_appgw, name_route_table_appgw)
routes_appgw = route_table_appgw.routes

rotas_comparacao_aks = []
rotas_comparacao_appgw = []

dicionario_rotas_aks = {}
dicionario_rotas_appgw = {}

for rota in routes_aks:
    dicionario_rotas_aks[rota.address_prefix] = rota

for rota in routes_appgw:
    dicionario_rotas_appgw[rota.address_prefix] = rota

for rota in routes_aks:
    rotas_comparacao_aks.append(rota)

for rota in rotas_comparacao_aks:
    if rota.address_prefix not in dicionario_rotas_appgw:
        rotas_comparacao_appgw.append(rota)

if len(rotas_comparacao_appgw) > 0:
    print("As seguintes rotas estão ausentes na tabela de rota do AppGw e serão adicionadas:")
    for rota in rotas_comparacao_appgw:
        print(f"- {rota.name} ({rota.address_prefix})")

    route_table_appgw.routes = rotas_comparacao_appgw
    route_table_appgw = network_client_appgw.route_tables.begin_create_or_update(
        resource_group_appgw, name_route_table_appgw, route_table_appgw
    ).result()
    print("Rotas adicionadas com sucesso!")
else:
    print("As tabelas de rotas do AKS e do AppGw já estão sincronizadas.")
