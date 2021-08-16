defmodule PolititweetWeb.PageController do
  use PolititweetWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end
