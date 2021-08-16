defmodule PolitiTweet.Repo do
  use Ecto.Repo,
    otp_app: :polititweet,
    adapter: Ecto.Adapters.Postgres
end
