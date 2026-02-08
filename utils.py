import random

def shuffle_vocab(word_pairs):
    items = []
    for i, (word, meaning) in enumerate(word_pairs):
        items.append({'val': word, 'type': 'W', 'id': i})
        items.append({'val': meaning, 'type': 'M', 'id': i})

    max_attempts = 2000 
    
    for _ in range(max_attempts):
        random.shuffle(items)
        result = []
        temp_pool = items[:]
        success = True
        
        while temp_pool:
            found_candidate = False
            # 매번 풀을 섞어서 다양한 조합 시도
            random.shuffle(temp_pool)
            
            for candidate in temp_pool:
                # 조건 1: 영단어 연속 최대 3개
                if candidate['type'] == 'W':
                    if len(result) >= 3 and all(r['type'] == 'W' for r in result[-3:]):
                        continue
                
                # 조건 2: 뜻 연속 최대 2개
                if candidate['type'] == 'M':
                    if len(result) >= 2 and all(r['type'] == 'M' for r in result[-2:]):
                        continue
                
                # 조건 3: 단어와 그 뜻은 최소 3개 이상 떨어져 있어야 함 (인덱스 차이 4 이상)
                # 현재 위치에 넣었을 때, 마지막 3개 중에 같은 id가 있으면 안됨
                last_ids = [r['id'] for r in result[-3:]]
                if candidate['id'] in last_ids:
                    continue
                
                result.append(candidate)
                temp_pool.remove(candidate)
                found_candidate = True
                break
            
            if not found_candidate:
                success = False
                break
        
        if success:
            return result
    return None
