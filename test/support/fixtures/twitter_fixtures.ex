defmodule PolitiTweet.TwitterFixtures do
  @moduledoc """
  This module defines test helpers for creating
  entities via the `PolitiTweet.Twitter` context.
  """

  @doc """
  Generate a user.
  """
  def user_fixture(attrs \\ %{}) do
    {:ok, user} =
      attrs
      |> Enum.into(%{
        twitter_id: "some twitter_id",
        username: "some username"
      })
      |> PolitiTweet.Twitter.create_user()

    user
  end
end
