import json
import heapq
import time
import math

def database():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def calcular_distancia(coord1, coord2):
    """Distância em linha reta entre duas coordenadas (lat, lon) usando a fórmula de Haversine."""
    R = 6371  # raio médio da Terra em km
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def construir_grafo(data, comercial):
    grafo = {}
    aeroportos = set()
    for cidade, info in data['municipios'].items():
        grafo[cidade] = list(info.get('vizinhos', {}).keys())
        if comercial == 's':
            if 'aeroporto' in info and info['aeroporto'].get('comercial', True):
                aeroportos.add(cidade)
        else:
            if 'aeroporto' in info:
                aeroportos.add(cidade)
    return grafo, aeroportos

def a_estrela(data, cidade_inicial, comercial):
    if cidade_inicial not in data['municipios']:
        return {'erro': 'Cidade não encontrada', 'tempo_ms': 0}

    inicio = time.time()
    grafo, aeroportos = construir_grafo(data, comercial)

    def heuristica(n):
        """Distância em linha reta até o aeroporto mais próximo"""
        coord_n = data['municipios'][n]['coordenadas']
        return min(
            calcular_distancia((coord_n['lat'], coord_n['lon']),
                               (data['municipios'][a]['coordenadas']['lat'],
                                data['municipios'][a]['coordenadas']['lon']))
            for a in aeroportos
        )

    fila = []
    heapq.heappush(fila, (heuristica(cidade_inicial), 0, cidade_inicial, [], 0))
    visitado = set()

    while fila:
        f, g, atual, caminho, distancia_total = heapq.heappop(fila)

        if atual in aeroportos:
            tempo_execucao = (time.time() - inicio) * 1000
            aeroporto_info = data['municipios'][atual]['aeroporto']
            return {
                'caminho': caminho + [atual],
                'distancia_total': distancia_total,
                'aeroporto': aeroporto_info['nome'],
                'iata': aeroporto_info.get('iata', 'N/A'),
                'tempo_ms': tempo_execucao
            }

        if atual in visitado:
            continue
        visitado.add(atual)

        for vizinho, dados in data['municipios'][atual].get('vizinhos', {}).items():
            nova_distancia = distancia_total + dados['distancia_km']
            novo_caminho = caminho + [atual]
            novo_g = g + 1
            novo_f = nova_distancia + heuristica(vizinho)
            heapq.heappush(fila, (novo_f, novo_g, vizinho, novo_caminho, nova_distancia))

    tempo_execucao = (time.time() - inicio) * 1000
    return {'erro': 'Nenhum aeroporto alcançável', 'tempo_ms': tempo_execucao}

def main():
    data = database()
    if not data:
        return

    print("\nSistema de Mapeamento de Aeroportos no Amazonas - Busca A* (com coordenadas)")
    print("------------------------------------------------------------------------")

    while True:
        comercial = input("\nDeseja consultar apenas aeroportos comerciais? (s/n): ").lower()
        while comercial not in ('s', 'n'):
            comercial = input("Digite apenas 's' ou 'n': ").lower()

        cidade = input("\nDigite o nome da cidade de origem (exatamente como no banco de dados): ").strip()
        resultado = a_estrela(data, cidade, comercial)

        if 'erro' in resultado:
            print(f"\nErro: {resultado['erro']}")
            print(f"Tempo de busca: {resultado['tempo_ms']:.4f} ms")
            continue

        print("\n" + "="*50)
        print(f"Rota a partir de: {cidade}")
        print("-"*50)
        print(f"• Aeroporto mais próximo: {resultado['aeroporto']} (Código IATA: {resultado['iata']})")
        print(f"• Caminho completo: {' → '.join(resultado['caminho'])}")
        print(f"• Distância total: {resultado['distancia_total']} km")
        print(f"• Tempo de busca: {resultado['tempo_ms']:.4f} ms")
        print("="*50)

        continuar = input("\nDeseja consultar outra cidade? (s/n): ").lower()
        if continuar != 's':
            break

if __name__ == "__main__":
    main()
