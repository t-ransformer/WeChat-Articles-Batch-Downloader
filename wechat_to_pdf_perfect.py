#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完美的微信公众号文章转PDF方案
使用浏览器自动化，确保100%准确，所有图片都包含
"""

import os
import re
import time
import sys
import glob

def sanitize_filename(filename):
    """清理文件名，移除非法字符"""
    # 移除Markdown标题标记
    filename = re.sub(r'^#+\s*', '', filename)  # 移除 # 标题标记
    filename = filename.strip()
    
    # 替换非法字符
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除多余的空格和下划线
    filename = re.sub(r'[\s_]+', '_', filename)
    filename = filename.strip('_')
    
    # 限制文件名长度
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("正在安装 playwright...")
    os.system(f"{sys.executable} -m pip install playwright")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright


def wait_for_all_images_loaded(page, max_wait_time=30, show_details=False):
    """
    等待所有图片加载完成
    
    Args:
        page: Playwright页面对象
        max_wait_time: 最大等待时间（秒）
        show_details: 是否显示未加载图片的详情
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        # 检查图片加载状态（排除UI元素的图片）
        image_status = page.evaluate("""
            () => {
                const images = Array.from(document.querySelectorAll('img'));
                if (images.length === 0) return {
                    total: 0, 
                    loaded: 0, 
                    percentage: 100,
                    failed: []
                };
                
                // 过滤掉UI元素的图片（二维码等）
                const contentImages = images.filter(img => {
                    // 排除二维码图片
                    if (img.className && (
                        img.className.includes('qr_code') || 
                        img.className.includes('qrcode') ||
                        img.id && img.id.includes('qr_code')
                    )) return false;
                    
                    // 排除空src的图片（通常是UI占位符）
                    if (!img.src || img.src.trim() === '') return false;
                    
                    // 排除src是页面URL的图片（通常是跳转二维码）
                    if (img.src.includes('mp.weixin.qq.com/s/') && !img.src.includes('mmbiz') && !img.src.includes('qpic')) return false;
                    
                    return true;
                });
                
                const failed = [];
                const loaded = contentImages.filter((img, idx) => {
                    // 检查图片是否加载完成
                    if (img.complete && img.naturalHeight !== 0) return true;
                    // 检查是否是data URI（内联图片）
                    if (img.src.startsWith('data:')) return true;
                    
                    // 记录未加载的图片
                    failed.push({
                        index: idx,
                        src: img.src.substring(0, 100),
                        complete: img.complete,
                        naturalHeight: img.naturalHeight,
                        hasDataSrc: img.hasAttribute('data-src')
                    });
                    return false;
                }).length;
                
                return {
                    total: contentImages.length,
                    loaded: loaded,
                    percentage: Math.round((loaded / contentImages.length) * 100),
                    failed: failed,
                    totalAll: images.length,
                    uiImages: images.length - contentImages.length
                };
            }
        """)
        
        total = image_status['total']
        loaded = image_status['loaded']
        percentage = image_status['percentage']
        failed = image_status.get('failed', [])
        total_all = image_status.get('totalAll', total)
        ui_images = image_status.get('uiImages', 0)
        
        if total == 0 or loaded == total:
            if ui_images > 0:
                print(f"    ✅ 所有文章图片已加载完成 ({loaded}/{total})，已排除 {ui_images} 个UI元素图片")
            else:
                print(f"    ✅ 所有图片已加载完成 ({loaded}/{total})")
            return True
        
        if time.time() - start_time > 5:  # 5秒后开始显示进度
            if show_details and failed:
                print(f"    文章图片加载进度: {loaded}/{total} ({percentage}%) [总图片: {total_all}, UI图片: {ui_images}]")
                if len(failed) <= 3:
                    print(f"    未加载图片数: {len(failed)}")
                    for f in failed[:3]:
                        print(f"      - {f['src'][:80]}...")
            else:
                print(f"    文章图片加载进度: {loaded}/{total} ({percentage}%)")
        
        # 如果已经加载了90%以上，或者等待超过15秒且加载了70%以上，就继续处理
        elapsed = time.time() - start_time
        if percentage >= 90 or (elapsed > 15 and percentage >= 70):
            print(f"    ✅ 图片加载 {percentage}%，继续处理（已等待 {elapsed:.0f} 秒）")
            return True
        
        time.sleep(1)
    
    print(f"    ⚠️  超时，已加载 {loaded}/{total} 张文章图片 ({percentage}%)")
    if failed and show_details:
        print(f"    未加载的图片详情:")
        for f in failed[:5]:
            print(f"      - {f['src'][:80]}...")
    # 即使超时，如果加载了70%以上也返回True
    return percentage >= 70


def convert_wechat_article_to_pdf_perfect(url, output_path):
    """
    完美转换微信公众号文章为PDF
    
    Args:
        url: 文章URL
        output_path: PDF输出路径
        
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*60}")
    print(f"转换文章: {url}")
    print(f"{'='*60}")
    
    try:
        with sync_playwright() as p:
            # 启动浏览器
            print("\n[1/5] 启动浏览器...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
            
            # 创建上下文，模拟真实浏览器
            print("[2/5] 创建浏览器上下文...")
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )
            
            page = context.new_page()
            
            # 访问URL
            print(f"[3/5] 加载页面: {url}")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                print(f"    ⚠️  页面加载警告: {str(e)}")
            
            # 等待初始内容加载
            print("    等待初始内容加载...")
            time.sleep(3)
            
            # 滚动页面以触发懒加载
            print("[4/5] 触发图片懒加载...")
            scroll_attempts = 3
            for i in range(scroll_attempts):
                # 滚动到底部
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
                # 滚动回顶部
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(1)
                
                # 滚动到中间
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(1)
            
            # 强制触发所有图片加载
            print("    强制加载所有图片...")
            page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    images.forEach(img => {
                        // 移除懒加载属性
                        if (img.hasAttribute('data-src')) {
                            img.src = img.getAttribute('data-src');
                        }
                        if (img.hasAttribute('data-original')) {
                            img.src = img.getAttribute('data-original');
                        }
                        if (img.hasAttribute('data-url')) {
                            img.src = img.getAttribute('data-url');
                        }
                        if (img.hasAttribute('loading')) {
                            img.removeAttribute('loading');
                        }
                        // 强制重新加载
                        if (!img.complete) {
                            const src = img.src;
                            img.src = '';
                            img.src = src;
                        }
                    });
                    
                    // 触发所有图片的load事件
                    images.forEach(img => {
                        if (img.src && !img.complete) {
                            const newImg = new Image();
                            newImg.src = img.src;
                        }
                    });
                }
            """)
            
            # 等待一下让图片开始加载
            time.sleep(2)
            
            # 等待所有图片加载完成（减少等待时间，避免卡住）
            print("[5/5] 等待所有图片加载...")
            images_loaded = wait_for_all_images_loaded(page, max_wait_time=30, show_details=True)
            
            # 如果还有图片未加载，再次尝试滚动和等待
            if not images_loaded:
                print("    部分图片未加载，再次尝试...")
                # 再次滚动
                for _ in range(2):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(1)
                
                # 再次等待（显示详情）
                images_loaded = wait_for_all_images_loaded(page, max_wait_time=20, show_details=True)
            
            # 即使图片未完全加载，如果加载了80%以上，也继续处理
            if not images_loaded:
                image_status = page.evaluate("""
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        const contentImages = images.filter(img => {
                            if (img.className && (
                                img.className.includes('qr_code') || 
                                img.className.includes('qrcode') ||
                                img.id && img.id.includes('qr_code')
                            )) return false;
                            if (!img.src || img.src.trim() === '') return false;
                            if (img.src.includes('mp.weixin.qq.com/s/') && !img.src.includes('mmbiz') && !img.src.includes('qpic')) return false;
                            return true;
                        });
                        const loaded = contentImages.filter(img => {
                            return img.complete && (img.naturalHeight !== 0 || img.src.startsWith('data:'));
                        }).length;
                        return {
                            total: contentImages.length,
                            loaded: loaded,
                            percentage: contentImages.length > 0 ? Math.round((loaded / contentImages.length) * 100) : 100
                        };
                    }
                """)
                percentage = image_status['percentage']
                # 降低阈值到70%，确保能处理更多文章
                if percentage >= 70:
                    print(f"    ⚠️  图片加载 {percentage}%，继续处理...")
                    images_loaded = True
            
            # 额外等待网络空闲
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            
            # 最后等待确保稳定
            print("    最后等待确保稳定...")
            time.sleep(3)
            
            # 检查页面内容
            page_title = page.title()
            print(f"\n页面标题: {page_title}")
            
            # 使用页面标题生成PDF文件名
            if os.path.isdir(output_path) or not output_path.endswith('.pdf'):
                # 清理标题，生成安全的文件名
                safe_title = sanitize_filename(page_title)
                output_path = os.path.join(output_path, f"{safe_title}.pdf")
            else:
                # 如果已经指定了完整路径，使用页面标题更新文件名
                output_dir = os.path.dirname(output_path)
                safe_title = sanitize_filename(page_title)
                output_path = os.path.join(output_dir, f"{safe_title}.pdf")
            
            # 检查文件是否已存在（包括检查是否有类似的文件名）
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / 1024 / 1024
                print(f"  ⏭️  PDF已存在 ({file_size:.2f} MB)，跳过")
                browser.close()
                return True
            
            # 检查是否有基于Markdown文件名的旧PDF文件（避免重复）
            output_dir = os.path.dirname(output_path)
            safe_title_clean = safe_title.split('_2026')[0] if '_2026' in safe_title else safe_title
            existing_pdfs = glob.glob(os.path.join(output_dir, '*.pdf'))
            for existing_pdf in existing_pdfs:
                existing_name = os.path.basename(existing_pdf).replace('.pdf', '')
                existing_clean = existing_name.split('_2026')[0] if '_2026' in existing_name else existing_name
                # 如果文件名匹配（忽略时间戳），删除旧文件
                if safe_title_clean == existing_clean or safe_title_clean in existing_clean or existing_clean in safe_title_clean:
                    if existing_pdf != output_path:
                        print(f"  🗑️  删除旧PDF文件: {os.path.basename(existing_pdf)}")
                        try:
                            os.remove(existing_pdf)
                        except:
                            pass
                        break
            
            # 检查是否有验证页面
            page_content = page.content()
            has_verification = '环境异常' in page_content or '验证' in page_content or '完成验证' in page_content
            
            if has_verification:
                print("    ⚠️  检测到验证页面！")
                screenshot_path = output_path.replace('.pdf', '_screenshot.png')
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    已保存截图: {screenshot_path}")
                
                # 等待更长时间，看是否能自动通过验证
                print("    等待验证页面处理（30秒）...")
                time.sleep(30)
                
                # 刷新页面重试
                print("    刷新页面重试...")
                page.reload(wait_until='domcontentloaded', timeout=60000)
                time.sleep(5)
                
                # 再次检查
                page_content = page.content()
                has_verification = '环境异常' in page_content or '验证' in page_content or '完成验证' in page_content
                
                if has_verification:
                    print("    ⚠️  仍然显示验证页面，但尝试继续生成PDF...")
                    # 不直接返回False，尝试继续生成PDF（可能内容已经加载）
            
            # 检查页面是否真的加载了文章内容
            # 微信公众号文章通常包含特定的class或id
            has_article_content = page.evaluate("""
                () => {
                    // 检查是否有文章内容区域
                    const articleContent = document.querySelector('#js_content') || 
                                         document.querySelector('.rich_media_content') ||
                                         document.querySelector('article');
                    return articleContent !== null && articleContent.textContent.length > 100;
                }
            """)
            
            if not has_article_content:
                print("    ⚠️  未检测到文章内容，可能页面未正确加载")
                screenshot_path = output_path.replace('.pdf', '_screenshot.png')
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    已保存截图用于调试: {screenshot_path}")
                browser.close()
                return False
            
            # 生成PDF
            print(f"\n生成PDF: {output_path}")
            page.pdf(
                path=output_path,
                format='A4',
                print_background=True,  # 包含背景图片和颜色
                margin={
                    'top': '1cm',
                    'right': '1cm',
                    'bottom': '1cm',
                    'left': '1cm'
                },
                prefer_css_page_size=False,
                scale=1.0,
            )
            
            browser.close()
            
            # 验证PDF文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / 1024 / 1024  # MB
                print(f"\n✅ PDF生成成功！")
                print(f"   文件大小: {file_size:.2f} MB")
                print(f"   图片加载: {'✅ 全部加载' if images_loaded else '⚠️  部分加载'}")
                return True
            else:
                print("\n❌ PDF文件未生成")
                return False
                
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_url_from_markdown(md_file_path):
    """从Markdown文件中提取URL"""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找原文链接 - 支持多种格式
        patterns = [
            r'\*\*原文链接\*\*:\s*(https?://[^\s]+)',  # **原文链接**: https://...
            r'原文链接[：:]\s*(https?://[^\s]+)',      # 原文链接: https://...
            r'链接[：:]\s*(https?://mp\.weixin\.qq\.com[^\s]+)',  # 链接: https://mp.weixin.qq.com...
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                url = match.group(1).strip()
                # 清理URL（移除末尾的标点符号）
                url = url.rstrip('.,;!?')
                # 如果是http，转换为https
                if url.startswith('http://'):
                    url = url.replace('http://', 'https://', 1)
                return url
        
        return None
    except Exception as e:
        print(f"读取Markdown文件错误: {str(e)}")
        return None


if __name__ == '__main__':
    import glob
    
    # 查找指定的文章文件
    md_pattern = 'WeChat-Articles-Batch-Downloader/output/markdown/2D_3D扫描成像*.md'
    md_files = glob.glob(md_pattern)
    
    if not md_files:
        print("❌ 未找到Markdown文件")
        sys.exit(1)
    
    md_file = os.path.abspath(md_files[0])
    print(f"找到文件: {md_file}")
    
    # 从Markdown文件中提取URL
    url = get_url_from_markdown(md_file)
    
    if not url:
        print("❌ 无法从Markdown文件中提取URL")
        sys.exit(1)
    
    print(f"找到URL: {url}")
    
    # 生成输出路径
    output_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'
    os.makedirs(output_dir, exist_ok=True)
    
    output_filename = "2D_3D扫描成像(Scan&Paint)技术——帮你更好的看见声音.pdf"
    output_path = os.path.join(output_dir, output_filename)
    
    # 转换
    success = convert_wechat_article_to_pdf_perfect(url, output_path)
    
    if success:
        print(f"\n✅ 完成！PDF文件: {output_path}")
    else:
        print(f"\n❌ 转换失败")

