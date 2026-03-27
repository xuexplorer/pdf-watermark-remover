#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF旋转水印去除工具
去除PDF中的旋转/斜体文字水印，保留正文完整
"""
import pikepdf
import os
import re
import argparse
from pathlib import Path


def remove_rotated_watermark(input_path: str, output_path: str, rotation_threshold: float = 0.01) -> int:
    """
    去除PDF中的旋转水印
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        rotation_threshold: 旋转检测阈值，默认0.01
    
    Returns:
        去除的水印块数量
    """
    pdf = pikepdf.open(input_path)
    watermark_count = 0
    
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        
        if "/Contents" not in page:
            continue
        
        # 获取内容流
        contents = page.Contents
        if isinstance(contents, pikepdf.Array):
            content_streams = []
            for ref in contents:
                try:
                    stream = pdf.get_object(ref.objgen)
                    content_streams.append(stream.read_bytes())
                except:
                    pass
            content_bytes = b"\n".join(content_streams)
        else:
            try:
                content_bytes = contents.read_bytes()
            except:
                continue
        
        # 解码内容流
        try:
            content_str = content_bytes.decode('latin-1')
        except:
            continue
        
        # 查找并删除旋转文本块
        bt_et_pattern = r'BT\s+(.*?)\s+ET'
        
        def process_bt_block(match):
            nonlocal watermark_count
            block = match.group(0)
            
            # 检查是否包含旋转矩阵
            # Tm a b c d e f，其中b和c不为0表示旋转
            tm_pattern = r'Tm\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)'
            tm_matches = list(re.finditer(tm_pattern, block))
            
            for tm_match in tm_matches:
                b = float(tm_match.group(2))
                c = float(tm_match.group(3))
                
                # 如果b或c不为0，说明有旋转
                if abs(b) > rotation_threshold or abs(c) > rotation_threshold:
                    watermark_count += 1
                    return ''  # 返回空字符串删除块
            
            return block
        
        new_content = re.sub(bt_et_pattern, process_bt_block, content_str, flags=re.DOTALL)
        
        if new_content != content_str:
            new_stream = pikepdf.Stream(pdf, new_content.encode('latin-1'))
            page.Contents = new_stream
    
    # 保存
    pdf.save(output_path)
    pdf.close()
    
    return watermark_count


def batch_remove_watermark(source_dir: str, target_dir: str, rotation_threshold: float = 0.01) -> dict:
    """
    批量去除PDF水印
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        rotation_threshold: 旋转检测阈值
    
    Returns:
        处理结果统计
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # 确保目标目录存在
    target_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有PDF文件
    pdf_files = list(source_path.glob("*.pdf"))
    
    results = {
        "total": len(pdf_files),
        "success": 0,
        "failed": 0,
        "total_watermarks": 0,
        "errors": []
    }
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 处理: {pdf_file.name}")
        
        output_file = target_path / pdf_file.name
        
        try:
            count = remove_rotated_watermark(
                str(pdf_file),
                str(output_file),
                rotation_threshold
            )
            results["success"] += 1
            results["total_watermarks"] += count
            print(f"  去除水印: {count} 处 [OK]")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{pdf_file.name}: {str(e)}")
            print(f"  [FAIL] {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="PDF旋转水印去除工具")
    parser.add_argument("-i", "--input", help="输入PDF文件路径")
    parser.add_argument("-o", "--output", help="输出PDF文件路径")
    parser.add_argument("-s", "--source", help="源目录（批量处理）")
    parser.add_argument("-t", "--target", help="目标目录（批量处理）")
    parser.add_argument("--threshold", type=float, default=0.01, help="旋转检测阈值（默认0.01）")
    
    args = parser.parse_args()
    
    if args.input and args.output:
        # 单文件处理
        print(f"处理文件: {args.input}")
        count = remove_rotated_watermark(args.input, args.output, args.threshold)
        print(f"去除水印: {count} 处")
        print(f"输出文件: {args.output}")
    
    elif args.source and args.target:
        # 批量处理
        print(f"批量处理: {args.source} -> {args.target}")
        results = batch_remove_watermark(args.source, args.target, args.threshold)
        print("\n" + "=" * 60)
        print(f"处理完成:")
        print(f"  总计: {results['total']} 个文件")
        print(f"  成功: {results['success']} 个")
        print(f"  失败: {results['failed']} 个")
        print(f"  去除水印: {results['total_watermarks']} 处")
        
        if results["errors"]:
            print("\n错误详情:")
            for error in results["errors"]:
                print(f"  - {error}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
