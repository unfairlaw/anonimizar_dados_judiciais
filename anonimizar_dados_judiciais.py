import random

def generate_random_name_pf():
    # Sílabas para formar nomes fictícios
    words = names_and_surnames_pt_br = ["João Silva", "Maria Santos", "Carlos Oliveira", "Ana Souza", "José Pereira", "Fernanda Costa", "Paulo Santana", "Amanda Martins", "Pedro Ferreira", "Juliana Gonçalves", "Lucas Rodrigues", "Camila Almeida", "Marcelo Nascimento", "Patrícia Lima", "Rafael Carvalho", "Mariana Gomes", "Fábio Dias", "Laura Barbosa", "Diego Mendes", "Bianca Fernandes", "Bruno Rocha", "Tatiane Araújo", "Anderson Sales", "Gabriela Ribeiro", "Renato Cavalcanti", "Adriana Monteiro", "Leandro Correia", "Débora Marques", "Thiago Pereira", "Isabela Campos", "Felipe Cardoso", "Carolina Moreira", "Gustavo Lopes", "Aline Santos", "Vinícius Oliveira", "Natalia Silveira", "Eduardo Freitas", "Larissa Vieira", "Rodrigo Sousa", "Michelle Pinto", "Ricardo Costa", "Vanessa Dantas", "Marcela Barros", "André Melo", "Jéssica Farias", "Guilherme Araujo", "Priscila Ferreira", "Leonardo Sampaio", "Fernanda Lima"]


    # Gerar um nome com 3 sílabas para cada uma das 3 palavras
    name_pf = [random.choice(words) for _ in range(1)]
    name_pf = ' '.join(word.capitalize() for word in name_pf)

    return name_pf

def generate_random_prof():
    # Sílabas para formar profissões fictícias
    words = brazilian_professions = ["Médico", "Advogado", "Professor", "Engenheiro", "Enfermeiro", "Farmacêutico", "Administrador", "Psicólogo", "Contador", "Técnico em Informática", "Vendedor", "Eletricista", "Mecânico", "Arquiteto", "Fisioterapeuta", "Dentista", "Analista de Sistemas", "Estudante", "Técnico em Enfermagem", "Designer", "Pedreiro", "Nutricionista", "Policial", "Garçom", "Motorista", "Bombeiro", "Piloto", "Cabeleireiro", "Agricultor", "Jornalista", "Técnico em Segurança do Trabalho", "Recepcionista", "Técnico em Eletrônica", "Padeiro", "Cozinheiro", "Atendente", "Músico", "Operador de Máquinas", "Programador", "Auxiliar Administrativo", "Analista Financeiro", "Técnico em Radiologia", "Designer Gráfico", "Faxineiro", "Operário", "Promotor de Vendas", "Consultor de Vendas", "Taxista", "Zelador"]

    # Gerar um nome com 3 sílabas para cada uma das 3 palavras
    prof_pf = [random.choice(words) for _ in range(1)]
    prof_pf = ' '.join(word.capitalize() for word in prof_pf)

    return prof_pf

def generate_random_name_pj():
    # Sílabas para formar nomes fictícios
    company_names_pt_br = ["Construções Futuro S.A.", "TechSoluções Ltda.", "Inovação Digital & Cia.", "Energia Verde Incorporadora", "Mundo das Ideias Consultoria", "Qualidade Total Serviços Ltda.", "Vanguarda Tecnologia e Inovação", "Grupo Global Marketing", "Soluções Inteligentes Empreendimentos", "MasterComércio Importação e Exportação", "Conexão Criativa Publicidade", "Grupo Visionário Seguros", "Infraestrutura Digital Ltda.", "Sistema Integrado de Logística", "Tecnologia Avançada S.A.", "EcoTech Soluções Ambientais", "Grupo Progresso Construções", "Inovação em Saúde Ltda.", "Excelência Empresarial Consultoria", "Visão Futura Consultoria Financeira", "Planeta Verde Energia Renovável", "Companhia Digital de Educação", "Central de Negócios Global", "Mundo Empresarial Distribuidora", "AgroSoluções S.A.", "Consultoria Estratégica Global", "Vanguarda Ambiental Ltda.", "Grupo Prime Empreendimentos", "Inovação Tecnológica S.A.", "Construções Modernas Ltda.", "EcoLogística Transportes Sustentáveis", "TechInova Soluções em TI", "Futuro Seguro Corretora de Seguros", "Novo Horizonte Consultoria", "Soluções Criativas Marketing Digital", "Grupo Excelência Financeira", "Construções Sustentáveis Ltda.", "Inovação em Saúde Ltda.", "EcoTecnologia Ambiental", "Grupo Global Empreendimentos", "Logística Inteligente S.A.", "Inovação Digital Ltda.", "Soluções Integradas Tecnologia", "Energia do Futuro Ltda.", "Vanguarda Empreendimentos", "Grupo Verde Ambiental", "Consultoria Global de Negócios", "Soluções em Tecnologia Sustentável", "Empresa Visionária de TI", "Construções Modernas Ltda."]

    name_pj = [random.choice(company_names_pt_br) for _ in range(1)]
    name_pj = ' '.join(word.capitalize() for word in name_pj)
    return name_pj

def generate_random_cnpj():
    cnpj_root = [random.randint(0, 9) for _ in range(8)]
    cnpj_root = cnpj_root + [((sum([(5 - i) * v for i, v in enumerate(cnpj_root)]) % 11) % 10)]
    cnpj_root = cnpj_root + [((sum([(6 - i) * v for i, v in enumerate(cnpj_root)]) % 11) % 10)]

    cnpj = cnpj_root + [0, 0, 0, 1]  # Adding fixed digits for CNPJ format
    cnpj = cnpj + [((sum([(9 - i) * v for i, v in enumerate(cnpj)]) % 11) % 10)]
    cnpj = cnpj + [((sum([(10 - i) * v for i, v in enumerate(cnpj)]) % 11) % 10)]
    cnpj = '{:02d}.{:03d}.{:03d}/0001-{:02d}'.format(*map(int, cnpj))
    return cnpj

def generate_random_cpf():
    # Generate the first 9 digits
    digits = [random.randint(0, 9) for _ in range(9)]
    
    # Calculate first check digit
    sum1 = sum(d * (10 - i) for i, d in enumerate(digits))
    d1 = (sum1 * 10) % 11
    if d1 == 10:
        d1 = 0
    digits.append(d1)
    
    # Calculate second check digit
    sum2 = sum(d * (11 - i) for i, d in enumerate(digits))
    d2 = (sum2 * 10) % 11
    if d2 == 10:
        d2 = 0
    digits.append(d2)
    
    # Format into CPF string: XXX.XXX.XXX-XX
    cpf = '{:03d}.{:03d}.{:03d}-{:02d}'.format(
        int(''.join(map(str, digits[0:3]))),
        int(''.join(map(str, digits[3:6]))),
        int(''.join(map(str, digits[6:9]))),
        int(''.join(map(str, digits[9:11])))
    )
    
    return cpf

def generate_random_rg():
    rg = '{:03d}.{:03d}.{:03d}-{:02d}'.format(random.randint(0, 999), random.randint(0, 999), random.randint(0, 999), random.randint(0, 99))
    return rg

def generate_random_oabn():
    # Gerar número OAB
    oab_n = '{:03d}.{:03d}'.format(random.randint(0, 999), random.randint(0, 999))
    
    # Escolher um estado aleatoriamente
    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE"]
    estado = random.choice(estados)
    
    # Combinar número OAB com o estado
    oab_with_state = '{}/{}'.format(oab_n, estado)
    
    return oab_with_state

def generate_random_name_adv():
    # Sílabas para formar nomes fictícios
    adv_names_pt_br = ["Júlio César", "Augusto", "Marco Antônio", "Cícero", "Pompeu", "Brutus", "Sêneca", "Tibério Graco", "Caio Graco", "Lúcio Cornélio Sula", "Catão, o Jovem", "Catão, o Velho", "Marco Licínio Crasso", "Clódio", "Mário", "Lívio Druso", "Lúcio Sérgio Catilina", "Cláudio Marcelo", "Marco Emílio Lépido", "Márcio Rex", "Públio Clódio Pulcro", "Lúcio Cornélio Cina", "Cneu Pompeu Magno", "Marco Licínio Lúculo", "Lúcio Cornélio Sula Félix", "Quinto Hortênsio Hórtalo", "Marco Antônio Orador", "Marco Fúlvio Nobilior", "Quinto Cecílio Metelo", "Mânio Aquílio", "Caio Verres", "Caio Otávio Turino", "Quinto Fábio Máximo Verrucoso", "Marco Terêncio Varrão", "Caio Escribônio Curio", "Públio Cornélio Cipião Nasica", "Marco Calpúrnio Bíbulo", "Marco Emílio Escauro", "Lúcio Cornélio Cinna", "Caio Júlio César", "Lúcio Júnio Bruto", "Públio Valério Publícola", "Públio Clódio Pulcro", "Marco Cláudio Marcelo", "Caio Papírio Carbão", "Caio Papírio Carbão", "Públio Clódio Pulcro", "Caio Júlio César Otaviano", "Marco Antônio Orador", "Públio Cornélio Cipião Africano", "Hans Kelsen", "Rudolf Stammler", "Eugen Ehrlich", "Georges Gurvitch", "Léon Duguit", "José Ortega y Gasset", "H. L. A. Hart", "John Chipman Gray", "Max Radin", "Roscoe Pound", "Karl Renner", "Giorgio Del Vecchio", "Eduard Gans", "Robert von Mohl", "Gustav Radbruch", "Otto Bauer", "Julius Binder", "Edmond Picard", "Karl Binding", "Ernesto Teodoro Moneta", "Nikolay Korkunov", "Hans Gross", "Edouard Lambert", "Gustav Schmoller", "Albert Venn Dicey", "Franz von Liszt", "Émile Durkheim", "Henry Maine", "Eugenio María de Hostos", "Anatole Leroy-Beaulieu", "Julius Binder", "Henry Sidgwick", "Ferdinand Lassalle", "Othmar Spann", "Friedrich Karl von Savigny", "Giuseppe Ferrari", "Johann Kaspar Bluntschli", "Karl von Amira", "Enrico Ferri", "Eugen Huber", "Leopold von Ranke", "Antonio Labriola", "Francisco Giner de los Ríos", "Miguel Antonio Caro", "John Neville Figgis", "Henry Demarest Lloyd", "Louis Brandeis", "Harold Laski", "Giuseppe Mazzini", "Félix Houphouët-Boigny", "Jeremy Bentham", "Georges Scelle", "Adolf Merkl", "Giuseppe Bettiol", "Eugenio Rignano", "Dugald Stewart", "André Tunc", "Carlo Calisse", "Giovanni Gentile", "Gabriele De Rosa", "Sir Henry Sumner Maine", "Giorgio La Pira", "Julius Stone", "Johann Georg Walch", "Franz Xaver von Schwarz", "Franz von Holtzendorff", "Eduard Maurer", "Harold J. Laski", "Felix Kaufmann", "Antonio Gramsci", "Edward Jenks", "Adolphe Quételet", "Franz von Liszt", "Otto von Gierke", "Konrad Hesse", "Otto Kirchheimer", "Heinrich Brunner", "Gaetano Filangieri", "Francesco Carrara", "August von Bulmerincq", "Hermann Kantorowicz", "Hermann Heller", "John Austin", "Henry Reeve", "Gustav Radbruch", "Antonio Rosmini-Serbati", "Miguel de Unamuno", "Antonio Sánchez de Bustamante", "Francisco Suárez", "Carlos Cossio", "Norberto Bobbio", "Panagiotis Kanellopoulos", "Eugenio María de Hostos", "Francisco de Vitoria", "Edmond Picard", "John Dewey", "Gustav Radbruch", "Hans Kelsen", "Léon Duguit", "H. L. A. Hart"]

    name_adv = [random.choice(adv_names_pt_br) for _ in range(1)]
    name_adv = ' '.join(word.capitalize() for word in name_adv)
    return name_adv

def generate_petition_addressaut():
    streets = ["Avenida Paulista City", "Rua Augusta Town", "Rua 25 de Março Ville", "Avenida Atlântica Metropolis", "Rua Oscar Freire Township", "Avenida Brasil City", "Rua das Flores Village", "Avenida Presidente Vargas Heights", "Rua do Lavradio Borough", "Rua da Consolação Municipality", "Avenida Copacabana Township", "Rua Barão de Itapetininga Metropolis", "Avenida Faria Lima City", "Rua Teodoro Sampaio Township", "Rua Sete de Setembro Town", "Avenida Rebouças District", "Rua José Paulino Village", "Avenida Rio Branco Metropolis", "Rua João Cachoeira City", "Avenida Getúlio Vargas Borough", "Rua Visconde de Pirajá Municipality", "Avenida Brigadeiro Luís Antônio Township", "Rua Marechal Deodoro Town", "Avenida Nove de Julho Heights", "Rua Bela Cintra City", "Avenida das Américas Township", "Rua Xavier de Toledo District", "Avenida Juscelino Kubitschek Metropolis", "Rua Barão de Limeira Borough", "Rua Marechal Floriano Ville", "Avenida Paulista City", "Rua Augusta Town", "Rua 25 de Março Ville", "Avenida Atlântica Metropolis", "Rua Oscar Freire Township", "Avenida Brasil City", "Rua das Flores Village", "Avenida Presidente Vargas Heights", "Rua do Lavradio Borough", "Rua da Consolação Municipality", "Avenida Copacabana Township", "Rua Barão de Itapetininga Metropolis", "Avenida Faria Lima City", "Rua Teodoro Sampaio Township", "Rua Sete de Setembro Town", "Avenida Rebouças District", "Rua José Paulino Village", "Avenida Rio Branco Metropolis", "Rua João Cachoeira City", "Avenida Getúlio Vargas Borough", "Rua Principal", "Avenida Central", "Travessa das Flores", "Rua dos Girassóis", "Avenida dos Ipês"]
    cities = ["Fortaleza", "Recife", "Curitiba", "Porto Alegre", "Manaus", "Belém", "Goiânia", "Guarulhos", "Campinas", "São Luís", "São Gonçalo", "Maceió", "Duque de Caxias", "Nova Iguaçu", "São Bernardo do Campo", "Teresina", "Natal", "Campo Grande", "Osasco", "Santo André", "João Pessoa", "Jaboatão dos Guararapes", "São José dos Campos", "Ribeirão Preto", "Uberlândia", "Contagem", "Sorocaba", "Aracaju", "Feira de Santana", "Cuiabá", "Joinville", "Juiz de Fora", "Londrina", "Aparecida de Goiânia", "Ananindeua", "Niterói", "São João de Meriti", "Porto Velho", "Belford Roxo", "Serra", "Caxias do Sul", "Campos dos Goytacazes", "Florianópolis", "Vila Velha", "Mauá", "São José do Rio Preto", "Macapá", "Santos", "Betim", "Mogi das Cruzes"]
    states = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE"]

    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    number = random.randint(1, 1000)
    cep = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    petition_addressaut = f"{street}, {number}, {city} - {state}. CEP {cep}"
    return petition_addressaut

def generate_petition_addressreu():
    streets = ["Avenida Paulista", "Rua Augusta", "Rua 25 de Março", "Avenida Atlântica", "Rua Oscar Freire", "Avenida Brasil", "Rua das Flores", "Avenida Presidente Vargas", "Rua do Lavradio", "Rua da Consolação", "Avenida Copacabana", "Rua Barão de Itapetininga", "Avenida Faria Lima", "Rua Teodoro Sampaio", "Rua Sete de Setembro", "Avenida Rebouças", "Rua José Paulino", "Avenida Rio Branco", "Rua João Cachoeira", "Avenida Getúlio Vargas", "Rua Visconde de Pirajá", "Avenida Brigadeiro Luís Antônio", "Rua Marechal Deodoro", "Avenida Nove de Julho", "Rua Bela Cintra", "Avenida das Américas", "Rua Xavier de Toledo", "Avenida Juscelino Kubitschek", "Rua Barão de Limeira", "Rua Marechal Floriano"]
    cities = ["São Paulo", "Rio de Janeiro", "Salvador", "Brasília", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Goiânia", "Belém", "Porto Alegre", "São Luís", "Guarulhos", "Campinas", "São Gonçalo", "São Bernardo do Campo", "Nova Iguaçu", "Duque de Caxias", "Natal", "Teresina", "São João de Meriti", "Campo Grande", "Osasco", "Santo André", "João Pessoa", "Jaboatão dos Guararapes", "Contagem", "Ribeirão Preto", "São José dos Campos"]
    states = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN","RS", "RO", "RR", "SC", "SP", "SE"]

    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    number = random.randint(1, 1000)
    cep = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    petition_addressreu = f"{street}, {number}, {city} - {state}. CEP {cep}"
    return petition_addressreu

def generate_petition_addressadv():
    streets = ["Avenida Paulista", "Rua Augusta", "Rua 25 de Março", "Avenida Atlântica", "Rua Oscar Freire", "Avenida Brasil", "Rua das Flores", "Avenida Presidente Vargas", "Rua do Lavradio", "Rua da Consolação", "Avenida Copacabana", "Rua Barão de Itapetininga", "Avenida Faria Lima", "Rua Teodoro Sampaio", "Rua Sete de Setembro", "Avenida Rebouças", "Rua José Paulino", "Avenida Rio Branco", "Rua João Cachoeira", "Avenida Getúlio Vargas", "Rua Visconde de Pirajá", "Avenida Brigadeiro Luís Antônio", "Rua Marechal Deodoro", "Avenida Nove de Julho", "Rua Bela Cintra", "Avenida das Américas", "Rua Xavier de Toledo", "Avenida Juscelino Kubitschek", "Rua Barão de Limeira", "Rua Marechal Floriano"]
    cities = ["São Paulo", "Rio de Janeiro", "Salvador", "Brasília", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Goiânia", "Belém", "Porto Alegre", "São Luís", "Guarulhos", "Campinas", "São Gonçalo", "São Bernardo do Campo", "Nova Iguaçu", "Duque de Caxias", "Natal", "Teresina", "São João de Meriti", "Campo Grande", "Osasco", "Santo André", "João Pessoa", "Jaboatão dos Guararapes", "Contagem", "Ribeirão Preto", "São José dos Campos"]
    states = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN","RS", "RO", "RR", "SC", "SP", "SE"]

    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    number = random.randint(1, 1000)
    cep = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    petition_addressadv = f"{street}, {number}, {city} - {state}. CEP {cep}"
    return petition_addressadv

def generate_petition_citydate():
    cities = ["São Paulo", "Rio de Janeiro", "Salvador", "Brasília", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Goiânia", "Belém", "Porto Alegre", "São Luís", "Guarulhos", "Campinas", "São Gonçalo", "São Bernardo do Campo", "Nova Iguaçu", "Duque de Caxias", "Natal", "Teresina", "São João de Meriti", "Campo Grande", "Osasco", "Santo André", "João Pessoa", "Jaboatão dos Guararapes", "Contagem", "Ribeirão Preto", "São José dos Campos"]
    states = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN","RS", "RO", "RR", "SC", "SP", "SE"]
    months = ['janeiro', 'fevereiro','março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

    city = random.choice(cities)
    state = random.choice(states)
    day = random.randint(1, 30)
    month = random.choice(months)
    year = random.randint(2000, 3000)
    
    citydate = f"{city}, {state}, {day} de {month} de {year}."
    return citydate

def generate_petition_dateshoursdif():
    
    weekdays = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    day = random.randint(1, 30)
    month = random.randint(1, 12)
    year = random.randint(2000, 3000)
    hour = random.randint(00, 24)
    minute = random.randint (00, 60)
    second = random.randint (00, 60)
    weekday = random.choice(weekdays)
        
    dateshoursdif = f"{day:02d}/{month:02d}/{year:04d} {weekday} - {hour:02d}:{minute:02d}:{second:02d}"
    return dateshoursdif

def generate_random_judicial_process():
    
    NNNNNNN = random.randint(1000000, 9999999)
    DD = random.randint(1, 99)
    AAAA = random.randint(2000, 2023)
    J = random.randint(1, 9)
    TR = random.randint(1, 99)
    
    OOOO = random.randint(1, 9999)

    # Formata para o padrão de processo judicial sem as letras 'J' e 'TR'
    judicial_process = f"{NNNNNNN:07d}-{DD:02d}.{AAAA}.{J}.{TR:02d}.{OOOO:04d}"
    return judicial_process

def generate_random_bankaccount():
    
    brazilian_banks = ['Banco do Brasil', 'Caixa Econômica Federal', 'Banco Bradesco', 'Itaú Unibanco', 'Santander Brasil', 'Banco BTG Pactual', 'Banco Inter', 'Banco Safra', 'Banco Original', 'Banco Santander']
    credit_card_companies = ['Visa', 'Mastercard', 'American Express', 'Elo', 'Diners Club', 'Discover', 'Hipercard']
    
    bank = random.choice(brazilian_banks)
    agency = random.randint(111, 999)
    agdigit1 = random.randint(1, 9) 
    agdigit2 = random.randint(0, 9) 
    account1 = random.randint(000, 999)
    account2 = random.randint(000, 999)
    accdigit = random.randint(0, 9)
    creditcard1 = random.randint(1111, 9999)
    creditcard2 = random.randint(1111, 9999)
    creditcard3 = random.randint(1111, 9999)
    creditcard4 = random.randint(1111, 9999)
    creditcardcompany = random.choice(credit_card_companies)
    month = random.randint(1, 12)
    year = random.randint(00,99)
    
    bankaccount = f"{bank}, agência {agdigit1:01d}.{agency:03d}-{agdigit2} / {account1:03d}.{account2:03}-{accdigit} / {creditcardcompany} {creditcard1:4d}.{creditcard2:4d}.{creditcard3:4d}.{creditcard4:4d} Validade: {month:02d}/{year:02d}"
    return bankaccount

def generate_telephone():
    
    ddd1 = random.randint(00, 99)
    telef1 = random.randint(11111, 99999)
    telef2 = random.randint(1111, 9999)
    ddd2 = random.randint(00, 99)
    telef3 = random.randint(11111, 99999)
    telef4 = random.randint(1111, 9999)
    ddd3 = random.randint(00, 99)
    telef5 = random.randint(11111, 99999)
    telef6 = random.randint(1111, 9999)
    ddd4 = random.randint(00, 99)
    telef7 = random.randint(11111, 99999)
    telef8 = random.randint(1111, 9999)
    
        # Formata para o padrão de processo judicial sem as letras 'J' e 'TR'
    telephones = f"({ddd1:02d}) {telef1:05d}-{telef2:04d}  / ({ddd2:02d}) {telef3:05d}-{telef4:04d} / ({ddd3:02d}) {telef5:05d}-{telef6:04d} / ({ddd4:02d}) {telef7:05d}-{telef8:04d}"
    return telephones


def generate_petition_data():
    name_pf = generate_random_name_pf()
    name_pj = generate_random_name_pj()
    cnpj = generate_random_cnpj()
    cpf = generate_random_cpf()
    rg = generate_random_rg()
    advN = generate_random_name_adv()
    oabn = generate_random_oabn()
    petition_addressaut = generate_petition_addressaut()
    petition_addressreu = generate_petition_addressreu()
    petition_addressadv = generate_petition_addressadv()
    prof_pf = generate_random_prof()
    judicial_process = generate_random_judicial_process()
    citydate = generate_petition_citydate()
    dateshoursdif = generate_petition_dateshoursdif()
    bankacc = generate_random_bankaccount()
    telephones = generate_telephone()
   

    petition_data = {
        "namePF": name_pf,
        "namepfcaps": name_pf.upper(),
        "namePJ": name_pj,
        "namepjcaps": name_pj.upper(),
        "cnpj": cnpj,
        "cpf": cpf,
        "rg": rg,
        "advN": advN,
        "advncaps": advN.upper(),
        "oabn": oabn,
        "petition_addressaut": petition_addressaut,
        "petition_addressreu": petition_addressreu,
        "petition_addressadv":petition_addressadv,
        "profPF":prof_pf,        
        "judicialprocess": judicial_process,
        "citydate": citydate,
        "datehours": dateshoursdif,
        "bankacc": bankacc,
        "phone": telephones,
    }
    return petition_data


petition_data = generate_petition_data()
print("Nome PF Aleatório:", petition_data["namePF"])
print("CPF Aleatório:", petition_data["cpf"])
print("RG Aleatório:", petition_data["rg"])
print("Profissão Aleatória:", petition_data["profPF"])
print("Endereço de Petição Aleatório Autor:", petition_data["petition_addressaut"])
print("----------------------------------------------------------------------------------------------------")
print("Nome PJ Aleatório:", petition_data["namePJ"])
print(petition_data["namepjcaps"])
print("CNPJ Aleatório:", petition_data["cnpj"])
print("Endereço de Petição Aleatório Reu:", petition_data["petition_addressreu"])
print("----------------------------------------------------------------------------------------------------")
print("Nome Adv:", petition_data["advN"])
print(petition_data["advncaps"])
print("OAB número:", petition_data["oabn"])
print("Endereço advogado:", petition_data["petition_addressadv"])
print("----------------------------------------------------------------------------------------------------")
print("Local, Data:", petition_data["citydate"])
print("Processo judicial aleatório:", petition_data["judicialprocess"])
print("Data e hora:", petition_data["datehours"])
print("----------------------------------------------------------------------------------------------------")
print("Banco:", petition_data["bankacc"])
print("----------------------------------------------------------------------------------------------------")
print ("Telefones:", petition_data["phone"])
print(petition_data["namepfcaps"])
