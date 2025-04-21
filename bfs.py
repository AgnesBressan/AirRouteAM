#para rodar utilize os seguintes comandos
#cd AirRouteAM
#python3 bfs.py
#quando o programa iniciar digite 's' para buscar por aeroportos comerciais ou n para aeroportos gerais
#após, digite o nome da cidade que você deseja buscar pelo aeroporto mais próximo (digite o nome como está no arquivo database.json)


from collections import deque
import json
import time

#carregando a base de dados database.json
def database():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

#funcao que realiza a busca em largura
def bfs(data, cidade_inicial, comercial):
    if cidade_inicial not in data['municipios']: #verifica se a cidade digitada esta no banco de dados
        return {'erro': 'Cidade não encontrada', 'tempo_ms': 0}  
    
    inicio = time.time() #marca o tempo de início da busca 
    
    fila = deque()
    fila.append((cidade_inicial, [], 0)) #adiciona a tupla que armazena cidade inicial, caminho percorrido e distancia
    visitados = set() #cidades ja visitadas

    while fila: 
        cidade, caminho, distancia_total = fila.popleft()
        
        if cidade in visitados:
            continue
        visitados.add(cidade)

        #verificacao do tipo de aeroporto escolhido pelo usuario
        if comercial == 's':
            if 'aeroporto' in data['municipios'][cidade] and data['municipios'][cidade]['aeroporto'].get('comercial', True):
                aeroporto = True
            else:
                aeroporto = False
        else:
            if 'aeroporto' in data['municipios'][cidade]:
                aeroporto = True
            else:
                aeroporto = False

        #caso seja encontrado o aeroporto ele retorna caminho, distancia, aeroporto, iata e tempo
        if aeroporto:
            tempo_execucao = (time.time() - inicio) * 1000
            return {
                'caminho': caminho + [cidade],
                'distancia_total': distancia_total,
                'aeroporto': data['municipios'][cidade]['aeroporto']['nome'],
                'iata': data['municipios'][cidade]['aeroporto'].get('iata', 'N/A'),
                'tempo_ms': tempo_execucao
            }
        
        #para cada cidade vizinha, a função tenta explorar os vizinhos e adicionar à fila de busca
        for vizinho, dados in data['municipios'][cidade].get('vizinhos', {}).items():
            nova_distancia = distancia_total + dados['distancia_km']
            fila.append((vizinho, caminho + [cidade], nova_distancia))
    
    #caso nao encontre nenhum aeroporto
    tempo_execucao = (time.time() - inicio) * 1000
    return {'erro': 'Nenhum aeroporto alcançável', 'tempo_ms': tempo_execucao}

#funcao principal que chama a funcao bfs e exibe o resultado 
def main():
    data = database()
    if not data:
        return
    
    print("\nSistema de Mapeamento de Aeroportos no Amazonas")
    print("---------------------------------------------")
    
    while True:
        comercial = input("\nDeseja consultar apenas aeroportos comerciais? (s/n): ").lower()
        while comercial not in ('s', 'n'):
            comercial = input("Digite apenas 's' ou 'n': ").lower()
        
        cidade = input("\nDigite o nome da cidade de origem (exatamente como no banco de dados): ").strip()  
        resultado = bfs(data, cidade, comercial)
        
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