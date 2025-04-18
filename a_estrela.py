
import json
import heapq
import time

def database():
    with open('database_atualizado.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def gerar_heuristica(grafo, aeroportos):
    heuristica = {no: float('inf') for no in grafo}
    fila = list(aeroportos)
    for aeroporto in fila:
        heuristica[aeroporto] = 0
    while fila:
        atual = fila.pop(0)
        for vizinho in grafo.get(atual, []):
            if heuristica[vizinho] > heuristica[atual] + 1:
                heuristica[vizinho] = heuristica[atual] + 1
                fila.append(vizinho)
    return heuristica

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
    heuristica = gerar_heuristica(grafo, aeroportos)

    fila = []
    heapq.heappush(fila, (heuristica[cidade_inicial], 0, cidade_inicial, [], 0))  # (f, g, atual, caminho, distancia_total)
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
            novo_f = novo_g + heuristica[vizinho]
            heapq.heappush(fila, (novo_f, novo_g, vizinho, novo_caminho, nova_distancia))

    tempo_execucao = (time.time() - inicio) * 1000
    return {'erro': 'Nenhum aeroporto alcançável', 'tempo_ms': tempo_execucao}

def main():
    data = database()
    if not data:
        return

    print("\nSistema de Mapeamento de Aeroportos no Amazonas - Busca A*")
    print("----------------------------------------------------------")
    
    while True:
        comercial = input("\nDeseja consultar apenas aeroportos comerciais? (s/n): ").lower()
        while comercial != 's'and comercial != 'n':
            comercial = input("\nDeseja consultar apenas aeroportos comerciais? (s/n): ").lower()
        
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
