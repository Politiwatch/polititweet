defmodule Polititweet.Repo.Migrations.CreateUsers do
  use Ecto.Migration

  def change do
    create table(:users) do
      add :username, :string
      add :twitter_id, :string

      timestamps()
    end
  end
end
