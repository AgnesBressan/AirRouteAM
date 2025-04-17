from collections import deque
import json
import time  

def database():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def bfs(data, cidade_inicial):
    if cidade_inicial not in data['municipios']:
        return None
    
    inicio = time.time()  # Marca o início da execução
    
    fila = deque()
    fila.append((cidade_inicial, [], 0))  # (cidade_atual, caminho, distancia_total)
    visitados = set()

    while fila:
        cidade, caminho, distancia_total = fila.popleft()
        
        if cidade in visitados:
            continue
        visitados.add(cidade)

        # Verifica se a cidade atual tem aeroporto
        if 'aeroporto' in data['municipios'][cidade]:
            tempo_execucao = (time.time() - inicio) * 1000  # Calcula o tempo em milissegundos
            return {
                'caminho': caminho + [cidade],
                'distancia_total': distancia_total,
                'aeroporto': data['municipios'][cidade]['aeroporto']['nome'],
                'iata': data['municipios'][cidade]['aeroporto'].get('iata', 'N/A'),
                'tempo_ms': tempo_execucao  # Adiciona o tempo ao resultado
            }
        
        # Explora os vizinhos
        for vizinho, dados in data['municipios'][cidade].get('vizinhos', {}).items():
            nova_distancia = distancia_total + dados['distancia_km']
            fila.append((vizinho, caminho + [cidade], nova_distancia))
    
    tempo_execucao = (time.time() - inicio) * 1000
    return {'tempo_ms': tempo_execucao}  # Retorna o tempo mesmo se não encontrar

def main():
    data = database()
    if not data:
        return
    
    print("\nSistema de Mapeamento de Aeroportos no Amazonas")
    print("---------------------------------------------")
    
    while True:
        cidade = input("\nDigite o nome da cidade de origem (exatamente como no banco de dados): ").strip()  
        resultado = bfs(data, cidade)
        
        if not resultado or 'caminho' not in resultado:
            print(f"\nErro: Cidade '{cidade}' não encontrada ou não conectada a um aeroporto.")
            if 'tempo_ms' in resultado:
                print(f"Tempo de busca: {resultado['tempo_ms']:.4f} ms")
            continue
            
        print("\n" + "="*50)
        print(f"Rota a partir de: {cidade}")
        print("-"*50)
        print(f"• Aeroporto mais próximo: {resultado['aeroporto']} (Código IATA: {resultado['iata']})")
        print(f"• Caminho completo: {' → '.join(resultado['caminho'])}")
        print(f"• Distância total: {resultado['distancia_total']} km")
        print(f"• Tempo de busca: {resultado['tempo_ms']:.4f} ms")  # Mostra o tempo formatado
        print("="*50)

        continuar = input("\nDeseja consultar outra cidade? (s/n): ").lower()
        if continuar != 's':
            break

if __name__ == "__main__":
    main()