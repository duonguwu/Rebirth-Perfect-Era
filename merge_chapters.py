#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def merge_chapters(start, end, output_file):
    """Merge chapter files from start to end into output_file"""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for chapter_num in range(start, end + 1):
            input_file = f'vn_sub/chapter_{chapter_num}.txt'
            try:
                with open(input_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n\n')  # Add spacing between chapters
                print(f'✓ Merged chapter {chapter_num}')
            except FileNotFoundError:
                print(f'✗ File not found: {input_file}')

if __name__ == '__main__':
    start_chapter = int(input('Chương bắt đầu: '))
    end_chapter = int(input('Chương kết thúc: '))
    output_name = input(f'Tên file output (mặc định: {start_chapter}to{end_chapter}.txt): ').strip()
    
    if not output_name:
        output_name = f'{start_chapter}to{end_chapter}.txt'
    
    output_path = f'merge/{output_name}'
    merge_chapters(start_chapter, end_chapter, output_path)
    print(f'\n✓ Hoàn thành! File đã được lưu tại: {output_path}')
