defmodule PolitiTweetWeb.PageController do
  use PolitiTweetWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end
