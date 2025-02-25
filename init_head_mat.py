
import numpy as np
from scipy.sparse import csr_matrix
import json, sys


def read_identities(file, chunk_size=10000):

    """
    Read large similarity files in chunks to manage memory better
    """

    #Get unique headers
    headers = set()
    with open(file, 'r') as fr:
        for i, line in enumerate(fr):
            if i % chunk_size == 0:
                print(f'Processed {i} lines for headers...')
            seq1, seq2, _ = line.strip().split(' ')
            headers.add(seq1)
            headers.add(seq2)

    #Create index mapping
    headers = sorted(headers)
    index_dict = {key: idx for idx, key in enumerate(headers)}
    n = len(headers)

    #Initialise sparse matrix components
    rows = []
    cols = []
    data = []

    #Process file in chunks for matrix
    with open(file, 'r') as fr:
        chunk = []
        counter = 1
        for i, line in enumerate(fr):
            if i % chunk_size == 0:
                print(f'Processed {i} lines for matrix...')
            chunk.append(line)

            if len(chunk) >= chunk_size:
                process_chunk(chunk, index_dict, rows, cols, data)
                chunk = []
                counter += 1
        
        #Processing remaining lines
        if chunk:
            print('Processing remaining lines...')
            process_chunk(chunk, index_dict, rows, cols, data)

    #Create final sparse matrix
    mat = csr_matrix((data, (rows, cols)), shape=(n, n))

    return mat, headers


def process_chunk(chunk, index_dict, rows, cols, data):

    """
    Process a chunk a lines and update matrix components
    """

    for line in chunk:
        
        seq1, seq2, value = line.strip().split(' ')
        #Map index from seq names
        i = index_dict[seq1]
        j = index_dict[seq2]
        value = float(value)

        #Store each value and its symmetrix counterpart
        rows.extend([i, j])
        cols.extend([j, i])
        data.extend([value, value])


def save_head_mat(mat, headers, measure):

    file_mapping = {
        1: ('id_headings.json', 'id_mat.npy'),
        2: ('sim_headings.json', 'sim_mat.npy'),
        3: ('tm_headings.json', 'tm_mat.npy')
    }

    measures = file_mapping.keys() if measure == 0 else [measure]

    for m in measures:
        if m in file_mapping:
            header_file, mat_file = file_mapping[m]
            
            with open(header_file, 'w') as outfile:
                json.dump(list(headers), outfile)
            
            np.save(mat_file, mat.toarray())


if __name__ == '__main__':
    mat, headers = read_identities(sys.argv[1])
    save_head_mat(mat, headers, int(sys.argv[2]))