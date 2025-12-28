"""Terminal UI for interactive restaurant search using Textual framework."""

from __future__ import annotations

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import DataTable
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Input
from textual.widgets import RadioButton
from textual.widgets import RadioSet
from textual.widgets import Static

from .restaurant import Restaurant
from .restaurant import SortType
from .search import SearchRequest


class SearchPanel(Container):
    """搜尋輸入面板"""

    def compose(self) -> ComposeResult:
        """建立搜尋面板的元件"""
        yield Static("餐廳搜尋", classes="panel-title")
        with Horizontal(id="input-row"):
            yield Input(placeholder="地區 (例如: 東京)", id="area-input")
            yield Input(placeholder="關鍵字 (例如: 寿司)", id="keyword-input")
        with Horizontal(id="sort-row"):
            yield Static("排序:", classes="sort-label")
            with RadioSet(id="sort-radio"):
                yield RadioButton("評分排名", value=True, id="sort-ranking")
                yield RadioButton("評論數", id="sort-review")
                yield RadioButton("新開幕", id="sort-new")
                yield RadioButton("標準", id="sort-standard")
        yield Button("搜尋", variant="primary", id="search-button")


class ResultsTable(DataTable):
    """餐廳結果列表"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"

    def on_mount(self) -> None:
        """初始化表格欄位"""
        self.add_columns("餐廳名稱", "評分", "評論數", "地區", "類型")


class DetailPanel(Container):
    """餐廳詳細資訊面板"""

    def compose(self) -> ComposeResult:
        """建立詳細資訊面板的元件"""
        yield Static("詳細資訊", classes="panel-title")
        yield Static("請選擇餐廳查看詳細資訊", id="detail-content")


class TabelogApp(App):
    """Tabelog 餐廳搜尋 TUI 應用程式"""

    CSS = """
    Screen {
        layout: vertical;
    }

    .panel-title {
        background: $surface-darken-1;
        color: $text;
        padding: 1;
        text-align: center;
        text-style: bold;
    }

    SearchPanel {
        height: auto;
        border: solid $primary-lighten-1;
        padding: 1;
        margin: 1;
    }

    #input-row {
        height: auto;
        margin: 1;
        padding: 1;
    }

    #area-input, #keyword-input {
        width: 1fr;
        margin-right: 1;
    }

    #area-input:focus, #keyword-input:focus {
        border: solid $success;
    }

    #sort-row {
        height: auto;
        margin: 0 1 1 1;
        padding: 1;
    }

    #content-row {
        height: 1fr;
        margin: 0 1 1 1;
    }

    ResultsTable {
        width: 2fr;
        height: 100%;
        border: solid $primary-lighten-1;
        margin-right: 1;
    }

    ResultsTable:focus {
        border: solid $accent;
    }

    ResultsTable > .datatable--header {
        background: $surface-darken-1;
        color: $text;
        text-style: bold;
    }

    ResultsTable > .datatable--cursor {
        background: $accent-darken-1;
        color: $text;
    }

    DetailPanel {
        width: 1fr;
        height: 100%;
        border: solid $primary-lighten-1;
        padding: 1;
    }

    .sort-label {
        width: auto;
        padding: 0 2 0 0;
        color: $text-muted;
        text-style: bold;
        content-align: center middle;
    }

    RadioSet {
        width: 1fr;
        padding: 0;
        background: transparent;
        layout: horizontal;
    }

    RadioButton {
        padding: 0 2;
        margin: 0;
        background: transparent;
        color: $text-muted;
    }

    RadioButton:hover {
        color: $text;
    }

    RadioButton.-selected {
        color: $success;
        text-style: bold;
    }

    Button {
        margin: 1;
        width: 100%;
    }

    Button:hover {
        background: $primary-darken-1;
    }

    Button:focus {
        border: solid $accent;
    }

    #detail-content {
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "focus_search", "Search"),
        ("r", "focus_results", "Results"),
        ("d", "focus_detail", "Detail"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.restaurants: list[Restaurant] = []
        self.selected_restaurant: Restaurant | None = None
        self.search_worker = None

    def compose(self) -> ComposeResult:
        """建立應用程式的元件"""
        yield Header()
        yield SearchPanel()
        with Horizontal(id="content-row"):
            yield ResultsTable(id="results-table")
            yield DetailPanel()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """處理按鈕點擊事件"""
        if event.button.id == "search-button":
            self.start_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """處理 Input Enter 鍵事件"""
        if event.input.id in ("area-input", "keyword-input"):
            self.start_search()

    def start_search(self) -> None:
        """啟動搜尋（取消之前的搜尋）"""
        # 取消之前的搜尋 worker
        if self.search_worker and not self.search_worker.is_finished:
            self.search_worker.cancel()

        # 啟動新的搜尋 worker
        self.search_worker = self.run_worker(self.perform_search())

    async def perform_search(self) -> None:
        """執行餐廳搜尋"""
        try:
            # 取得輸入值
            area_input = self.query_one("#area-input", Input)
            keyword_input = self.query_one("#keyword-input", Input)

            area = area_input.value.strip()
            keyword = keyword_input.value.strip()

            if not area and not keyword:
                detail_content = self.query_one("#detail-content", Static)
                detail_content.update("請輸入地區或關鍵字")
                return

            # 取得排序方式
            sort_radio = self.query_one("#sort-radio", RadioSet)
            pressed_button = sort_radio.pressed_button

            if pressed_button and pressed_button.id == "sort-review":
                sort_type = SortType.REVIEW_COUNT
                sort_name = "評論數排序"
            elif pressed_button and pressed_button.id == "sort-new":
                sort_type = SortType.NEW_OPEN
                sort_name = "新開幕"
            elif pressed_button and pressed_button.id == "sort-standard":
                sort_type = SortType.STANDARD
                sort_name = "標準排序"
            else:
                sort_type = SortType.RANKING
                sort_name = "評分排名"

            # 顯示搜尋中訊息
            detail_content = self.query_one("#detail-content", Static)
            search_params = f"地區: {area or '(無)'}, 關鍵字: {keyword or '(無)'}"
            detail_content.update(f"搜尋中 ({sort_name}): {search_params}...")

            # 建立搜尋請求（使用 Tabelog 的排序）
            request = SearchRequest(area=area, keyword=keyword, sort_type=sort_type)

            # 執行搜尋
            response = await request.search()

            if response.restaurants:
                self.restaurants = response.restaurants
                self.update_results_table()
                detail_content.update(
                    f"找到 {len(self.restaurants)} 家餐廳\n搜尋條件: {search_params}\n排序: {sort_name}"
                )
            else:
                self.restaurants = []
                table = self.query_one("#results-table", ResultsTable)
                table.clear()
                detail_content.update("沒有找到餐廳")

        except Exception as e:
            # 捕獲所有異常，包括搜尋被取消的情況
            try:
                detail_content = self.query_one("#detail-content", Static)
                detail_content.update(f"搜尋錯誤: {str(e)}")
            except Exception:
                # 如果連更新 UI 都失敗（例如應用程式正在關閉），就忽略
                pass

    def update_results_table(self) -> None:
        """更新結果表格"""
        try:
            table = self.query_one("#results-table", ResultsTable)
            table.clear()

            for restaurant in self.restaurants:
                rating = f"{restaurant.rating:.2f}" if restaurant.rating else "N/A"
                review_count = str(restaurant.review_count) if restaurant.review_count else "N/A"
                area = restaurant.area or "N/A"
                genres = ", ".join(restaurant.genres[:2]) if restaurant.genres else "N/A"

                table.add_row(restaurant.name, rating, review_count, area, genres)
        except Exception:
            # 忽略更新表格時的錯誤（例如在搜尋被取消時）
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """處理表格行選擇事件"""
        if event.cursor_row < len(self.restaurants):
            self.selected_restaurant = self.restaurants[event.cursor_row]
            self.update_detail_panel()

    def update_detail_panel(self) -> None:
        """更新詳細資訊面板"""
        if not self.selected_restaurant:
            return

        r = self.selected_restaurant

        detail_text = f"""名稱: {r.name}
評分: {r.rating if r.rating else "N/A"}
評論數: {r.review_count if r.review_count else "N/A"}
儲存數: {r.save_count if r.save_count else "N/A"}
地區: {r.area if r.area else "N/A"}
車站: {r.station if r.station else "N/A"}
距離: {r.distance if r.distance else "N/A"}
類型: {", ".join(r.genres) if r.genres else "N/A"}
午餐價格: {r.lunch_price if r.lunch_price else "N/A"}
晚餐價格: {r.dinner_price if r.dinner_price else "N/A"}
URL: {r.url}
"""

        detail_content = self.query_one("#detail-content", Static)
        detail_content.update(detail_text)

    def action_focus_search(self) -> None:
        """聚焦到搜尋輸入框"""
        area_input = self.query_one("#area-input", Input)
        area_input.focus()

    def action_focus_results(self) -> None:
        """聚焦到結果表格"""
        table = self.query_one("#results-table", ResultsTable)
        table.focus()

    def action_focus_detail(self) -> None:
        """聚焦到詳細資訊面板"""
        detail_panel = self.query_one(DetailPanel)
        detail_panel.focus()


def main():
    """啟動 TUI 應用程式"""
    app = TabelogApp()
    app.run()


if __name__ == "__main__":
    main()
