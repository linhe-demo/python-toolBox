import time

from playwright.sync_api import sync_playwright


def run():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # 无头模式
        page = browser.new_page()

        # 访问主页
        page.goto("https://www.ai-ysh.com/")

        # 等待 Vue 渲染完成
        page.wait_for_selector(".sampleImg")  # 替换为目标元素的 CSS 选择器

        # 滚动到目标元素
        showSlow(page, ".sampleImg")

        product_links = page.locator(".sampleImg").all() # 获取所有目标

        for index, link in enumerate(product_links):
            print(f"点击第 {index + 1} 个产品")
            print(
                "-----------------------------------------商品数据抓取开始----------------------------------------------")
            time.sleep(1)  # 适当暂停，模拟用户行为
            # 点击进入详情页
            link.click()

            # 这里可以抓取详情页内容
            print(page.title())  # 示例：打印详情页标题
            time.sleep(2)  # 停顿一下，防止操作太快
            res = showSlow(page, ".el-table__header-wrapper")
            if res is False:
                # 返回上一页
                page.go_back()
                # 滚动到目标元素
                showSlow(page, ".sampleImg")
                time.sleep(2)
                page.wait_for_selector(".sampleImg")  # 等待主页重新加载
                continue
            getPageInfo(page)

            time.sleep(2)
            # 返回上一页
            page.go_back()
            # 滚动到目标元素
            showSlow(page, ".sampleImg")
            time.sleep(2)
            page.wait_for_selector(".sampleImg")  # 等待主页重新加载

        browser.close()

def showSlow(page, target):
    res = True

    try:
        target_element = page.locator(target).first(timeout=3000)

        element_position = target_element.evaluate("el => el.getBoundingClientRect().top + window.scrollY")

        # 逐步滚动鼠标
        current_position = page.evaluate("window.scrollY")
        while current_position < element_position:
            page.mouse.wheel(0, 150)  # 模拟鼠标滚轮往下滚动 150 像素
            time.sleep(0.2)  # 等待 0.2 秒，模拟人手动滑动
            current_position = page.evaluate("window.scrollY")
    except Exception as e:
        res = False
        print("未找到相关元素")
    return res


def getPageInfo(page):
        # 抓取目标信息
        table = page.locator(".el-table__body")  # 选择表格元素
        rows = table.locator("tr").all()  # 获取所有行

        # 遍历表格的每一行
        for row in rows:
            cells = row.locator("td").all()  # 获取当前行的所有 <td>
            row_data = [cell.inner_text() for cell in cells]  # 提取文本内容
            print(row_data)

        print("-----------------------------------------商品数据抓取结束----------------------------------------------")




if __name__ == '__main__':

    print("开始爬取映山网站")
    run()





