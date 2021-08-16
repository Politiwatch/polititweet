defmodule Polititweet.Twitter.User do
  use Ecto.Schema
  import Ecto.Changeset

  schema "users" do
    field :twitter_id, :string
    field :username, :string

    timestamps()
  end

  @doc false
  def changeset(user, attrs) do
    user
    |> cast(attrs, [:username, :twitter_id])
    |> validate_required([:username, :twitter_id])
  end
end
