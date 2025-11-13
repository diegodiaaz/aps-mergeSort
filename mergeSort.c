#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <math.h>
#include <sys/time.h>
#include <windows.h>

#define MAX_FIELD_LENGTH 256
#define MAX_LINE_LENGTH 2048

// Estrutura para armazenar uma linha do CSV
typedef struct {
    char *id_bdq;
    char *foco_id;
    double lat;
    double lon;
    char *data_pas;
    char *pais;
    char *estado;
    char *municipio;
    char *bioma;
    char *linha_original;  // Guarda a linha original para escrever de volta
} Registro;

// Estrutura para estatísticas
typedef struct {
    long long comparacoes;
    long long movimentacoes;
    double tempo_execucao;
} Estatisticas;

// Variáveis globais para estatísticas
Estatisticas stats = {0, 0, 0.0};

// Enum para os campos
typedef enum {
    CAMPO_ID_BDQ = 1,
    CAMPO_FOCO_ID,
    CAMPO_LAT,
    CAMPO_LON,
    CAMPO_DATA_PAS,
    CAMPO_PAIS,
    CAMPO_ESTADO,
    CAMPO_MUNICIPIO,
    CAMPO_BIOMA
} CampoOrdenacao;

// Função para remover espaços em branco no início e fim
char* trim(char *str) {
    if (str == NULL) return NULL;
    
    // Remove espaços do início
    while (isspace((unsigned char)*str)) str++;
    
    if (*str == 0) return str;
    
    // Remove espaços do fim
    char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    
    end[1] = '\0';
    
    return str;
}

// Função para comparar registros baseado no campo selecionado
int comparar_registros(Registro *a, Registro *b, int campo) {
    stats.comparacoes++;
    
    switch(campo) {
        case CAMPO_ID_BDQ:
            return strcmp(a->id_bdq, b->id_bdq);
        case CAMPO_FOCO_ID:
            return strcmp(a->foco_id, b->foco_id);
        case CAMPO_LAT:
            if (a->lat < b->lat) return -1;
            if (a->lat > b->lat) return 1;
            return 0;
        case CAMPO_LON:
            if (a->lon < b->lon) return -1;
            if (a->lon > b->lon) return 1;
            return 0;
        case CAMPO_DATA_PAS:
            return strcmp(a->data_pas, b->data_pas);
        case CAMPO_PAIS:
            return strcmp(a->pais, b->pais);
        case CAMPO_ESTADO:
            return strcmp(a->estado, b->estado);
        case CAMPO_MUNICIPIO:
            return strcmp(a->municipio, b->municipio);
        case CAMPO_BIOMA:
            return strcmp(a->bioma, b->bioma);
        default:
            return 0;
    }
}

// Função merge do MergeSort
void merge(Registro *arr, int left, int middle, int right, int campo) {
    int n1 = middle - left + 1;
    int n2 = right - middle;
    
    // Criar arrays temporários
    Registro *L = (Registro*)malloc(n1 * sizeof(Registro));
    Registro *R = (Registro*)malloc(n2 * sizeof(Registro));
    
    // Copiar dados para os arrays temporários
    for (int i = 0; i < n1; i++) {
        L[i] = arr[left + i];
        stats.movimentacoes++;
    }
    for (int j = 0; j < n2; j++) {
        R[j] = arr[middle + 1 + j];
        stats.movimentacoes++;
    }
    
    // Merge dos arrays temporários de volta ao array original
    int i = 0, j = 0, k = left;
    
    while (i < n1 && j < n2) {
        if (comparar_registros(&L[i], &R[j], campo) <= 0) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        stats.movimentacoes++;
        k++;
    }
    
    // Copiar elementos restantes de L[], se houver
    while (i < n1) {
        arr[k] = L[i];
        stats.movimentacoes++;
        i++;
        k++;
    }
    
    // Copiar elementos restantes de R[], se houver
    while (j < n2) {
        arr[k] = R[j];
        stats.movimentacoes++;
        j++;
        k++;
    }
    
    free(L);
    free(R);
}

// Função MergeSort recursiva
void mergeSort(Registro *arr, int left, int right, int campo) {
    if (left < right) {
        int middle = left + (right - left) / 2;
        
        // Ordenar primeira e segunda metades
        mergeSort(arr, left, middle, campo);
        mergeSort(arr, middle + 1, right, campo);
        
        // Fazer merge das metades ordenadas
        merge(arr, left, middle, right, campo);
    }
}

// Função para parsear uma linha do CSV
Registro parsear_linha(char *linha) {
    Registro reg;
    char *linha_copia = strdup(linha);
    char *token;
    int campo_num = 0;
    
    // Guardar linha original
    reg.linha_original = strdup(linha);
    
    // Inicializar campos
    reg.id_bdq = NULL;
    reg.foco_id = NULL;
    reg.data_pas = NULL;
    reg.pais = NULL;
    reg.estado = NULL;
    reg.municipio = NULL;
    reg.bioma = NULL;
    
    token = strtok(linha_copia, ",");
    while (token != NULL && campo_num < 9) {
        token = trim(token);
        
        switch(campo_num) {
            case 0:
                reg.id_bdq = strdup(token);
                break;
            case 1:
                reg.foco_id = strdup(token);
                break;
            case 2:
                reg.lat = atof(token);
                break;
            case 3:
                reg.lon = atof(token);
                break;
            case 4:
                reg.data_pas = strdup(token);
                break;
            case 5:
                reg.pais = strdup(token);
                break;
            case 6:
                reg.estado = strdup(token);
                break;
            case 7:
                reg.municipio = strdup(token);
                break;
            case 8:
                reg.bioma = strdup(token);
                break;
        }
        
        campo_num++;
        token = strtok(NULL, ",");
    }
    
    free(linha_copia);
    return reg;
}

// Função para liberar memória de um registro
void liberar_registro(Registro *reg) {
    if (reg->id_bdq) free(reg->id_bdq);
    if (reg->foco_id) free(reg->foco_id);
    if (reg->data_pas) free(reg->data_pas);
    if (reg->pais) free(reg->pais);
    if (reg->estado) free(reg->estado);
    if (reg->municipio) free(reg->municipio);
    if (reg->bioma) free(reg->bioma);
    if (reg->linha_original) free(reg->linha_original);
}

// Função para contar linhas do arquivo
int contar_linhas(const char *nome_arquivo) {
    FILE *arquivo = fopen(nome_arquivo, "r");
    if (!arquivo) return 0;
    
    int count = 0;
    char linha[MAX_LINE_LENGTH];
    
    while (fgets(linha, sizeof(linha), arquivo)) {
        count++;
    }
    
    fclose(arquivo);
    return count;
}

// Função para ler o CSV
Registro* ler_csv(const char *nome_arquivo, int *total_registros, char **cabecalho) {
    FILE *arquivo = fopen(nome_arquivo, "r");
    if (!arquivo) {
        printf("Erro ao abrir o arquivo %s\n", nome_arquivo);
        return NULL;
    }
    
    char linha[MAX_LINE_LENGTH];
    int count = 0;
    
    // Ler cabeçalho
    if (fgets(linha, sizeof(linha), arquivo)) {
        *cabecalho = strdup(linha);
    }
    
    // Contar total de linhas para alocar memória
    int total_linhas = contar_linhas(nome_arquivo) - 1; // -1 para excluir cabeçalho
    Registro *registros = (Registro*)malloc(total_linhas * sizeof(Registro));
    
    // Voltar ao início e pular cabeçalho
    rewind(arquivo);
    if (fgets(linha, sizeof(linha), arquivo) == NULL) { // Pular cabeçalho
        fclose(arquivo);
        return NULL;
    }
    
    // Ler dados
    while (fgets(linha, sizeof(linha), arquivo)) {
        // Remover newline
        linha[strcspn(linha, "\n")] = 0;
        
        registros[count] = parsear_linha(linha);
        count++;
    }
    
    fclose(arquivo);
    *total_registros = count;
    return registros;
}

// Função para escrever CSV ordenado
void escrever_csv_ordenado(const char *nome_arquivo, Registro *registros, int total, char *cabecalho) {
    FILE *arquivo = fopen(nome_arquivo, "w");
    if (!arquivo) {
        printf("Erro ao criar arquivo de saída\n");
        return;
    }
    
    // Escrever cabeçalho
    fprintf(arquivo, "%s", cabecalho);
    
    // Escrever dados ordenados (reconstruindo a linha do CSV)
    for (int i = 0; i < total; i++) {
        fprintf(arquivo, "%s,%s,%12.6f,%12.6f,%s,%s,%s,%s,%s\n",
                registros[i].id_bdq,
                registros[i].foco_id,
                registros[i].lat,
                registros[i].lon,
                registros[i].data_pas,
                registros[i].pais,
                registros[i].estado,
                registros[i].municipio,
                registros[i].bioma);
    }
    
    fclose(arquivo);
}

// Função para salvar estatísticas
void salvar_estatisticas(const char *nome_arquivo, int campo, int total_registros) {
    FILE *arquivo = fopen(nome_arquivo, "w");
    if (!arquivo) {
        printf("Erro ao criar arquivo de estatísticas\n");
        return;
    }
    
    char *nome_campo[] = {
        "",
        "id_bdq",
        "foco_id",
        "lat",
        "lon",
        "data_pas",
        "pais",
        "estado",
        "municipio",
        "bioma"
    };
    
    fprintf(arquivo, "===== ESTATÍSTICAS DE EXECUÇÃO DO MERGESORT =====\n\n");
    fprintf(arquivo, "Arquivo processado: focos_br_sc_ref_2024.csv\n");
    fprintf(arquivo, "Total de registros: %d\n", total_registros);
    fprintf(arquivo, "Campo de ordenação: %s\n\n", nome_campo[campo]);
    
    fprintf(arquivo, "--- Métricas de Desempenho ---\n");
    fprintf(arquivo, "Tempo de execução da ordenação: %.6f segundos\n", stats.tempo_execucao);
    fprintf(arquivo, "Total de comparações: %lld\n", stats.comparacoes);
    fprintf(arquivo, "Total de movimentações: %lld\n", stats.movimentacoes);

    fprintf(arquivo, "\n===== FIM DAS ESTATÍSTICAS =====\n");
    
    fclose(arquivo);
    
    printf("\nEstatísticas salvas em: %s\n", nome_arquivo);
}

// Função para exibir menu
int exibir_menu() {
    int escolha;
    
    printf("\n===== MERGESORT PARA ORDENAÇÃO DE CSV =====\n");
    printf("\nEscolha o campo para ordenação:\n");
    printf("1. id_bdq\n");
    printf("2. foco_id\n");
    printf("3. lat (latitude)\n");
    printf("4. lon (longitude)\n");
    printf("5. data_pas (data de passagem)\n");
    printf("6. pais\n");
    printf("7. estado\n");
    printf("8. municipio\n");
    printf("9. bioma\n");
    printf("0. Sair\n");
    printf("\nOpção: ");
    
    if (scanf("%d", &escolha) != 1) {
        return 0;
    }
    return escolha;
}

int main() {
    SetConsoleOutputCP(65001);
    char *cabecalho = NULL;
    int total_registros = 0;
    int campo_ordenacao;
    
    // Exibir menu e obter escolha
    campo_ordenacao = exibir_menu();
    
    if (campo_ordenacao < 1 || campo_ordenacao > 9) {
        printf("Opção inválida ou saída solicitada.\n");
        return 0;
    }
    
    printf("\n--- Iniciando processamento ---\n");
    
    // Ler arquivo CSV
    printf("Lendo arquivo CSV...\n");
    Registro *registros = ler_csv("focos_br_sc_ref_2024.csv", &total_registros, &cabecalho);
    
    if (!registros) {
        printf("Erro ao ler o arquivo CSV\n");
        return 1;
    }
    
    printf("Total de registros lidos: %d\n", total_registros);
    
    // Resetar estatísticas
    stats.comparacoes = 0;
    stats.movimentacoes = 0;
    
    // Medir tempo de execução
    printf("Iniciando ordenação...\n");
    struct timeval inicio, fim;
    gettimeofday(&inicio, NULL);
    
    // Executar MergeSort
    mergeSort(registros, 0, total_registros - 1, campo_ordenacao);
    
    gettimeofday(&fim, NULL);
    stats.tempo_execucao = (fim.tv_sec - inicio.tv_sec) + 
                          (fim.tv_usec - inicio.tv_usec) / 1000000.0;
    
    printf("Ordenação concluída em %.6f segundos\n", stats.tempo_execucao);
    
    // Salvar arquivo ordenado
    printf("Salvando arquivo ordenado...\n");
    escrever_csv_ordenado("dados_ordenados.csv", registros, total_registros, cabecalho);
    
    // Salvar estatísticas
    salvar_estatisticas("estatisticas_execucao.txt", campo_ordenacao, total_registros);
    
    // Exibir resumo
    printf("\n===== RESUMO DA EXECUÇÃO =====\n");
    printf("Arquivo ordenado: dados_ordenados.csv\n");
    printf("Estatísticas: estatisticas_execucao.txt\n");
    printf("Tempo total: %.6f segundos\n", stats.tempo_execucao);
    printf("Comparações: %lld\n", stats.comparacoes);
    printf("Movimentações: %lld\n", stats.movimentacoes);
    
    // Liberar memória
    for (int i = 0; i < total_registros; i++) {
        liberar_registro(&registros[i]);
    }
    free(registros);
    free(cabecalho);
    
    printf("\nProcessamento concluído com sucesso!\n");
    
    return 0;
}