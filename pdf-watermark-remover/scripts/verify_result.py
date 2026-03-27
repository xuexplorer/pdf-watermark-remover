#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证PDF水印去除结果
"""
import fitz  # PyMuPDF
import os
from pathlib import Path


def verify_pdf(pdf_path: str) -> dict:
    """
    验证单个PDF文件的水印去除效果
    
    Args:
        pdf_path: PDF文件路径
    
    Returns:
        验证结果
    """
    try:
        doc = fitz.open(pdf_path)
        
        has_watermark_font = False
        total_text_length = 0
        watermark_texts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            total_text_length += len(text)
            
            # 检查是否还有水印字体
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                for line in block.get("lines", []):
                    dir_vec = line.get("dir", (1, 0))
                    # 只检查旋转的文本
                    if abs(dir_vec[1]) > 0.1:
                        for span in line.get("spans", []):
                            font = span.get("font", "")
                            text_content = span.get("text", "").strip()
                            if "STSong-Light" in font or "FangSong_GB2312" in font:
                                has_watermark_font = True
                                watermark_texts.append(text_content)
        
        doc.close()
        
        # 检查正文是否存在
        has_content = total_text_length > 100
        
        return {
            "ok": not has_watermark_font and has_content,
            "has_watermark_font": has_watermark_font,
            "has_content": has_content,
            "text_length": total_text_length,
            "watermark_samples": watermark_texts[:5]  # 最多显示5个示例
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def batch_verify(target_dir: str) -> None:
    """
    批量验证目录中的所有PDF文件
    
    Args:
        target_dir: 目标目录
    """
    target_path = Path(target_dir)
    pdf_files = list(target_path.glob("*.pdf"))
    pdf_files.sort()
    
    print(f"验证 {len(pdf_files)} 个PDF文件...")
    print("=" * 80)
    
    success_count = 0
    watermark_still_exists = 0
    content_missing = 0
    
    for pdf_file in pdf_files:
        result = verify_pdf(str(pdf_file))
        
        if result.get("ok"):
            success_count += 1
            status = "[OK]"
        else:
            if result.get("has_watermark_font"):
                watermark_still_exists += 1
                status = "[水印仍在]"
            elif not result.get("has_content"):
                content_missing += 1
                status = "[正文缺失]"
            else:
                status = f"[错误: {result.get('error', '未知')}]"
        
        filename = pdf_file.name[:60]
        text_length = result.get("text_length", 0)
        print(f"{status} {filename}... (文本长度: {text_length})")
        
        # 如果有残留水印，显示示例
        if result.get("watermark_samples"):
            for sample in result["watermark_samples"]:
                print(f"      水印示例: {sample}")
    
    print("=" * 80)
    print(f"验证完成:")
    print(f"  成功: {success_count}/{len(pdf_files)}")
    print(f"  水印仍在: {watermark_still_exists}")
    print(f"  正文缺失: {content_missing}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="验证PDF水印去除结果")
    parser.add_argument("-f", "--file", help="验证单个PDF文件")
    parser.add_argument("-d", "--directory", help="验证目录中的所有PDF文件")
    
    args = parser.parse_args()
    
    if args.file:
        result = verify_pdf(args.file)
        print(f"文件: {args.file}")
        print(f"状态: {'通过' if result['ok'] else '未通过'}")
        print(f"文本长度: {result.get('text_length', 0)}")
        if result.get("has_watermark_font"):
            print("水印残留示例:")
            for sample in result.get("watermark_samples", []):
                print(f"  - {sample}")
    
    elif args.directory:
        batch_verify(args.directory)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
